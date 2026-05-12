const WORKER_URL  = process.env.REACT_APP_R2_WORKER_URL;
const AUTH_TOKEN  = process.env.REACT_APP_R2_AUTH_TOKEN;
const PUBLIC_BASE = process.env.REACT_APP_R2_PUBLIC_BASE;

// Validate image file — returns { ok, error }
export const validateImageFile = (file, maxMB = 5) => {
  const allowed = ['image/jpeg','image/jpg','image/png','image/webp','image/gif'];
  if (!allowed.includes(file.type))
    return { ok: false, error: 'Invalid file type. Only JPEG, PNG, WebP and GIF allowed.' };
  if (file.size > maxMB * 1024 * 1024)
    return { ok: false, error: `File too large. Maximum size is ${maxMB}MB.` };
  return { ok: true, error: null };
};

// Generate unique filename
export const generateFileName = (file) => {
  const ts  = Date.now();
  const rnd = Math.random().toString(36).substring(2, 8);
  const ext = file.name.split('.').pop().toLowerCase();
  return `${ts}-${rnd}.${ext}`;
};

// Upload any file to R2 — returns Promise<{ ok, url, error }>
// Supports progress callback via XHR
export const uploadToR2 = (file, folder = 'uploads', onProgress = null) => {
  return new Promise((resolve) => {
    try {
      const fileName = generateFileName(file);
      const key      = `${folder}/${fileName}`;
      const endpoint = `${WORKER_URL}/upload/${encodeURIComponent(key)}`;

      const xhr = new XMLHttpRequest();

      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable)
            onProgress(Math.round((e.loaded / e.total) * 95));
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          if (onProgress) onProgress(100);
          resolve({ ok: true, url: `${PUBLIC_BASE}/${key}` });
        } else {
          resolve({ ok: false, error: `Upload failed (${xhr.status}): ${xhr.statusText}` });
        }
      });

      xhr.addEventListener('error', () =>
        resolve({ ok: false, error: 'Network error during upload — check R2 Worker URL.' })
      );
      xhr.addEventListener('abort', () =>
        resolve({ ok: false, error: 'Upload was cancelled.' })
      );

      xhr.open('PUT', endpoint);
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
      xhr.setRequestHeader('X-Auth-Token', AUTH_TOKEN);
      xhr.send(file);

    } catch (err) {
      resolve({ ok: false, error: err.message });
    }
  });
};

// Delete file from R2 by full URL or key
export const deleteFromR2 = async (fileUrlOrKey) => {
  try {
    const key = fileUrlOrKey.startsWith('http')
      ? fileUrlOrKey.replace(PUBLIC_BASE + '/', '')
      : fileUrlOrKey;
    const res = await fetch(`${WORKER_URL}/delete/${encodeURIComponent(key)}`, {
      method: 'DELETE',
      headers: { 'X-Auth-Token': AUTH_TOKEN },
    });
    return res.ok;
  } catch { return false; }
};

// Human-readable file size
export const fileSizeLabel = (bytes) => {
  if (!bytes) return '0 Bytes';
  const k = 1024;
  const s = ['Bytes','KB','MB','GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + s[i];
};
