"""
Deterministic, Resumable Content Generation Job Queue with Persistent Checkpointing & Crash Recovery.
"""
import os
import json
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger("ContentJobQueue")


class JobStatus(str, Enum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    VALIDATING = "VALIDATING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    RETRY = "RETRY"


class ContentType(str, Enum):
    NOTE = "NOTE"
    MCQ = "MCQ"


@dataclass
class GenerationJob:
    job_id: str
    subject_code: str
    unit_number: int
    topic_id: int
    topic_name: str
    unit_name: str
    content_type: ContentType
    batch_index: int = 1
    question_count: int = 5
    status: JobStatus = JobStatus.PENDING
    assigned_key: Optional[str] = None
    attempt_count: int = 0
    max_attempts: int = 4
    error_message: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    result_payload: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["content_type"] = self.content_type.value
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationJob":
        data_copy = dict(data)
        data_copy["content_type"] = ContentType(data_copy["content_type"])
        data_copy["status"] = JobStatus(data_copy["status"])
        return cls(**data_copy)


class ContentJobQueue:
    """
    Manages deterministic jobs across topics, ensuring 100% resumable operations and crash recovery.
    """

    def __init__(self, checkpoint_path: str = "groq_jobs_checkpoint.json"):
        self.checkpoint_path = checkpoint_path
        self.jobs: Dict[str, GenerationJob] = {}
        self.load_checkpoint()

    def build_deterministic_queue(
        self,
        curriculum: List[Dict[str, Any]],
        generate_notes: bool = True,
        generate_mcqs: bool = True,
        mcq_batches_per_topic: int = 1,
        mcqs_per_batch: int = 5,
    ) -> int:
        """
        Builds deterministic job IDs for every topic in the curriculum.
        Preserves existing APPROVED/COMPLETED jobs from previous runs.
        """
        created_count = 0
        topic_global_id = 1

        for subject in curriculum:
            code = subject["course_code"]
            for unit in subject.get("units", []):
                unit_num = unit["unit_number"]
                unit_name = unit["name"]
                for topic in unit.get("topics", []):
                    # Normalized topic name
                    topic_name = topic["name"] if isinstance(topic, dict) else str(topic)
                    
                    # 1. Deterministic Note Job
                    if generate_notes:
                        note_job_id = f"{code}-U{unit_num}-T{topic_global_id:03d}-NOTE"
                        if note_job_id not in self.jobs:
                            self.jobs[note_job_id] = GenerationJob(
                                job_id=note_job_id,
                                subject_code=code,
                                unit_number=unit_num,
                                topic_id=topic_global_id,
                                topic_name=topic_name,
                                unit_name=unit_name,
                                content_type=ContentType.NOTE,
                                created_at=time.time(),
                                updated_at=time.time(),
                            )
                            created_count += 1

                    # 2. Deterministic MCQ Batches
                    if generate_mcqs:
                        for b_idx in range(1, mcq_batches_per_topic + 1):
                            mcq_job_id = f"{code}-U{unit_num}-T{topic_global_id:03d}-MCQ-B{b_idx:02d}"
                            if mcq_job_id not in self.jobs:
                                self.jobs[mcq_job_id] = GenerationJob(
                                    job_id=mcq_job_id,
                                    subject_code=code,
                                    unit_number=unit_num,
                                    topic_id=topic_global_id,
                                    topic_name=topic_name,
                                    unit_name=unit_name,
                                    content_type=ContentType.MCQ,
                                    batch_index=b_idx,
                                    question_count=mcqs_per_batch,
                                    created_at=time.time(),
                                    updated_at=time.time(),
                                )
                                created_count += 1

                    topic_global_id += 1

        self.save_checkpoint()
        logger.info(
            f"ContentJobQueue populated. Total jobs: {len(self.jobs)} (Newly initialized: {created_count})."
        )
        return len(self.jobs)

    def recover_crashed_jobs(self) -> int:
        """Crash recovery: reset any jobs stuck in GENERATING or VALIDATING back to PENDING."""
        recovered = 0
        now = time.time()
        for job in self.jobs.values():
            if job.status in [JobStatus.GENERATING, JobStatus.VALIDATING, JobStatus.RETRY]:
                job.status = JobStatus.PENDING
                job.assigned_key = None
                job.updated_at = now
                recovered += 1
        if recovered > 0:
            logger.info(f"Crash Recovery: Reset {recovered} stale/interrupted jobs back to PENDING.")
            self.save_checkpoint()
        return recovered

    def get_pending_jobs(self, content_type: Optional[ContentType] = None, subject_code: Optional[str] = None) -> List[GenerationJob]:
        """Get all runnable jobs filtered by criteria."""
        pending = []
        for job in self.jobs.values():
            if job.status == JobStatus.PENDING and job.attempt_count < job.max_attempts:
                if content_type and job.content_type != content_type:
                    continue
                if subject_code and job.subject_code != subject_code:
                    continue
                pending.append(job)
        return pending

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        assigned_key: Optional[str] = None,
        error_message: Optional[str] = None,
        payload: Optional[Any] = None,
    ) -> None:
        """Update job status and persist state."""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = status
            job.updated_at = time.time()
            if assigned_key:
                job.assigned_key = assigned_key
            if error_message:
                job.error_message = error_message
            if payload is not None:
                job.result_payload = payload
            if status == JobStatus.GENERATING:
                job.attempt_count += 1

    def save_checkpoint(self) -> None:
        """Persist jobs state to local JSON file for resumption."""
        try:
            data = {job_id: job.to_dict() for job_id, job in self.jobs.items()}
            with open(self.checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save job queue checkpoint: {e}")

    def load_checkpoint(self) -> None:
        """Load persistent jobs state if file exists."""
        if os.path.exists(self.checkpoint_path):
            try:
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.jobs = {job_id: GenerationJob.from_dict(d) for job_id, d in data.items()}
                logger.info(f"Loaded {len(self.jobs)} jobs from checkpoint {self.checkpoint_path}.")
            except Exception as e:
                logger.warning(f"Could not load checkpoint {self.checkpoint_path}: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Aggregate summary of queue statuses."""
        stats = {
            "total": len(self.jobs),
            "pending": 0,
            "generating": 0,
            "approved": 0,
            "rejected": 0,
            "failed": 0,
            "notes_approved": 0,
            "mcqs_approved": 0,
        }
        for j in self.jobs.values():
            if j.status == JobStatus.PENDING:
                stats["pending"] += 1
            elif j.status == JobStatus.GENERATING:
                stats["generating"] += 1
            elif j.status == JobStatus.APPROVED:
                stats["approved"] += 1
                if j.content_type == ContentType.NOTE:
                    stats["notes_approved"] += 1
                elif j.content_type == ContentType.MCQ:
                    stats["mcqs_approved"] += 1
            elif j.status == JobStatus.REJECTED:
                stats["rejected"] += 1
            elif j.status == JobStatus.FAILED:
                stats["failed"] += 1
        return stats
