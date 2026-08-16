/**
 * Simple, robust in-memory & sessionStorage client-side cache layer
 * Prevents redundant fetches for static curriculum and problem data.
 */

interface CacheEntry<T> {
  data: T;
  expiry: number;
}

const memoryCache = new Map<string, CacheEntry<any>>();

export const clientCache = {
  get<T>(key: string): T | null {
    // 1. Memory cache
    const mem = memoryCache.get(key);
    if (mem && mem.expiry > Date.now()) {
      return mem.data as T;
    }
    if (mem) {
      memoryCache.delete(key);
    }

    // 2. SessionStorage cache
    try {
      const raw = sessionStorage.getItem(`sem_cache_${key}`);
      if (raw) {
        const entry: CacheEntry<T> = JSON.parse(raw);
        if (entry.expiry > Date.now()) {
          memoryCache.set(key, entry);
          return entry.data;
        }
        sessionStorage.removeItem(`sem_cache_${key}`);
      }
    } catch {
      // Ignore storage errors
    }

    return null;
  },

  set<T>(key: string, data: T, ttlSeconds: number = 300): void {
    const entry: CacheEntry<T> = {
      data,
      expiry: Date.now() + ttlSeconds * 1000,
    };
    memoryCache.set(key, entry);
    try {
      sessionStorage.setItem(`sem_cache_${key}`, JSON.stringify(entry));
    } catch {
      // Storage full or unavailable
    }
  },

  invalidate(keyPattern?: string): void {
    if (!keyPattern) {
      memoryCache.clear();
      try {
        const keys = Object.keys(sessionStorage);
        for (const k of keys) {
          if (k.startsWith('sem_cache_')) {
            sessionStorage.removeItem(k);
          }
        }
      } catch {}
      return;
    }

    // Invalidate matching keys
    for (const k of Array.from(memoryCache.keys())) {
      if (k.includes(keyPattern)) {
        memoryCache.delete(k);
      }
    }
    try {
      const keys = Object.keys(sessionStorage);
      for (const k of keys) {
        if (k.startsWith('sem_cache_') && k.includes(keyPattern)) {
          sessionStorage.removeItem(k);
        }
      }
    } catch {}
  },
};

/**
 * Cache-wrapped fetcher utility
 */
export async function withCache<T>(
  cacheKey: string,
  fetcher: () => Promise<T>,
  ttlSeconds: number = 300
): Promise<T> {
  const cached = clientCache.get<T>(cacheKey);
  if (cached !== null) {
    return cached;
  }
  const fresh = await fetcher();
  clientCache.set(cacheKey, fresh, ttlSeconds);
  return fresh;
}
