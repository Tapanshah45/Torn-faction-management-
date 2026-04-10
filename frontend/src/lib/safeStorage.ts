const memoryStore = new Map<string, string>();

const getStorage = (): Storage | null => {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    return window.localStorage;
  } catch {
    return null;
  }
};

const cookieGet = (key: string): string | null => {
  if (typeof document === 'undefined') {
    return null;
  }

  const pairs = document.cookie ? document.cookie.split('; ') : [];
  for (const pair of pairs) {
    const [name, ...rest] = pair.split('=');
    if (name === encodeURIComponent(key)) {
      return decodeURIComponent(rest.join('='));
    }
  }

  return null;
};

const cookieSet = (key: string, value: string): boolean => {
  if (typeof document === 'undefined') {
    return false;
  }

  try {
    document.cookie = `${encodeURIComponent(key)}=${encodeURIComponent(value)}; Path=/; SameSite=Lax; Max-Age=604800`;
    return cookieGet(key) !== null;
  } catch {
    return false;
  }
};

const cookieRemove = (key: string): boolean => {
  if (typeof document === 'undefined') {
    return false;
  }

  try {
    document.cookie = `${encodeURIComponent(key)}=; Path=/; Max-Age=0; SameSite=Lax`;
    return true;
  } catch {
    return false;
  }
};

export const safeStorage = {
  getItem(key: string): string | null {
    const storage = getStorage();
    if (storage) {
      try {
        const value = storage.getItem(key);
        if (value !== null) {
          return value;
        }
      } catch {
        // Continue to fallback stores.
      }
    }

    const cookieValue = cookieGet(key);
    if (cookieValue !== null) {
      return cookieValue;
    }

    return memoryStore.get(key) ?? null;
  },

  setItem(key: string, value: string): boolean {
    const storage = getStorage();
    let saved = false;

    if (storage) {
      try {
        storage.setItem(key, value);
        saved = true;
      } catch {
        // Continue to fallback stores.
      }
    }

    if (cookieSet(key, value)) {
      saved = true;
    }

    memoryStore.set(key, value);
    return saved || memoryStore.get(key) === value;
  },

  removeItem(key: string): boolean {
    const storage = getStorage();
    let removed = false;

    if (storage) {
      try {
        storage.removeItem(key);
        removed = true;
      } catch {
        // Continue to fallback stores.
      }
    }

    if (cookieRemove(key)) {
      removed = true;
    }

    memoryStore.delete(key);
    return removed || !memoryStore.has(key);
  },
};