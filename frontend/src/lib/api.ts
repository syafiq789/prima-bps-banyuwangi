const STORAGE_KEY = 'lentera_mitra_sync_v1';

export function formatRupiah(amount: number): string {
  return 'Rp ' + Math.round(amount || 0).toLocaleString('id-ID');
}

export async function apiFetch<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const isFormData = options.body instanceof FormData;
  const headers: Record<string, string> = isFormData
    ? {}
    : { 'Content-Type': 'application/json' };

  const res = await fetch(`/api/v1${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      ...headers,
      ...(options.headers as Record<string, string> | undefined),
    },
  });

  const data = await res.json().catch(() => ({ ok: false, message: 'Gagal membaca respons server.' }));
  if (!res.ok) {
    throw new Error(data.message || `HTTP ${res.status}`);
  }
  return data as T;
}

function readLocalSync() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { mitra: [], kegiatan: [], penugasan: [], evaluasi: [] };
    const parsed = JSON.parse(raw);
    return {
      mitra: Array.isArray(parsed.mitra) ? parsed.mitra : [],
      kegiatan: Array.isArray(parsed.kegiatan) ? parsed.kegiatan : [],
      penugasan: Array.isArray(parsed.penugasan) ? parsed.penugasan : [],
      evaluasi: Array.isArray(parsed.evaluasi) ? parsed.evaluasi : [],
    };
  } catch {
    return { mitra: [], kegiatan: [], penugasan: [], evaluasi: [] };
  }
}

function mergeByKey<T>(a: T[], b: T[], keyFn: (item: T) => string): T[] {
  const map = new Map<string, T>();
  a.forEach((item) => map.set(keyFn(item), item));
  b.forEach((item) => map.set(keyFn(item), item));
  return Array.from(map.values());
}

export async function syncEphemeralSnapshot(): Promise<void> {
  try {
    const fresh = await apiFetch<any>('/mitra/ephemeral-sync');
    if (fresh.ok) {
      const localData = readLocalSync();
      const merged = {
        mitra: mergeByKey(localData.mitra, fresh.mitra || [], (x: any) => x.id_sobat),
        kegiatan: mergeByKey(localData.kegiatan, fresh.kegiatan || [], (x: any) => x.kode_kegiatan),
        penugasan: mergeByKey(localData.penugasan, fresh.penugasan || [], (x: any) => `${x.id_sobat}::${x.kode_kegiatan}`),
        evaluasi: mergeByKey(localData.evaluasi, fresh.evaluasi || [], (x: any) => `${x.id_sobat}::${x.kode_kegiatan}`),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    }
  } catch {
    // Non-fatal
  }
}

export async function restoreEphemeralIfNeeded(counts?: { mitra: number; kegiatan: number; penugasan: number; evaluasi: number }): Promise<boolean> {
  try {
    const localData = readLocalSync();
    const needRestore =
      !counts ||
      localData.mitra.length > counts.mitra ||
      localData.kegiatan.length > counts.kegiatan ||
      localData.penugasan.length > counts.penugasan ||
      localData.evaluasi.length > counts.evaluasi;

    if (!needRestore) return false;
    const res = await apiFetch<any>('/mitra/ephemeral-sync', {
      method: 'POST',
      body: JSON.stringify(localData),
    });
    return Boolean(
      res.ok &&
        (res.restored_mitra > 0 ||
          res.restored_kegiatan > 0 ||
          res.restored_penugasan > 0 ||
          res.restored_evaluasi > 0)
    );
  } catch {
    return false;
  }
}
