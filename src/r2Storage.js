const WORKER_URL = process.env.REACT_APP_R2_WORKER_URL;
const AUTH_TOKEN = process.env.REACT_APP_R2_AUTH_TOKEN;
const PUBLIC_BASE = process.env.REACT_APP_R2_PUBLIC_BASE;

// Validate image file type and size
export const validateImageFile = (file) => {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Invalid file type. Only JPEG, PNG, WebP, and GIF are allowed.'
    };
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'File size too large. Maximum size is 5MB.'
    };
  }

  return { valid: true, error: null };
};

// Upload file to R2
export const uploadToR2 = async (file, fileName) => {
  const response = await fetch(`${WORKER_URL}/upload/${fileName}`, {
    method: 'PUT',
    headers: {
      'Content-Type': file.type,
      'X-Auth-Token': AUTH_TOKEN,
    },
    body: file,
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return `${PUBLIC_BASE}/${fileName}`;
};

// Delete file from R2
export const deleteFromR2 = async (fileName) => {
  const response = await fetch(`${WORKER_URL}/delete/${fileName}`, {
    method: 'DELETE',
    headers: {
      'X-Auth-Token': AUTH_TOKEN,
    },
  });

  if (!response.ok) {
    throw new Error('Delete failed');
  }

  return true;
};

// Generate unique filename
export const generateFileName = (file) => {
  const timestamp = Date.now();
  const randomStr = Math.random().toString(36).substring(2, 8);
  const extension = file.name.split('.').pop();
  return `${timestamp}-${randomStr}.${extension}`;
};

// Convert file size to readable label
export const fileSizeLabel = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};