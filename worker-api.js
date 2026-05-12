export default {
  async fetch(request, env) {

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Auth-Token',
        'Access-Control-Max-Age': '86400',
      }});
    }

    const CORS = { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' };
    const url  = new URL(request.url);
    const path = url.pathname;

    // Health check
    if (request.method === 'GET' && path === '/') {
      return new Response(JSON.stringify({ ok: true, service: 'AGBC R2 API v2' }), { headers: CORS });
    }

    // PUT /upload/{filename} → store in R2
    if (request.method === 'PUT' && path.startsWith('/upload/')) {
      const key = path.replace('/upload/', '');
      if (!key) return new Response(JSON.stringify({ ok:false, error:'No filename' }), { status:400, headers:CORS });
      await env.R2_BUCKET.put(key, request.body, {
        httpMetadata: { contentType: request.headers.get('Content-Type') || 'application/octet-stream' }
      });
      return new Response(JSON.stringify({ ok: true, key }), { headers: CORS });
    }

    // GET /file/{filename} → serve file from R2 with CORS
    if (request.method === 'GET' && path.startsWith('/file/')) {
      const key = path.replace('/file/', '');
      if (!key) return new Response('Missing filename', { status: 400, headers: { 'Access-Control-Allow-Origin': '*' } });
      const obj = await env.R2_BUCKET.get(key);
      if (!obj) return new Response('Not Found', { status: 404, headers: { 'Access-Control-Allow-Origin': '*' } });
      const headers = new Headers();
      headers.set('Access-Control-Allow-Origin', '*');
      headers.set('Cache-Control', 'public, max-age=86400');
      headers.set('Content-Type', obj.httpMetadata?.contentType || 'application/octet-stream');
      return new Response(obj.body, { headers });
    }

    // DELETE /delete/{filename} → remove from R2
    if (request.method === 'DELETE' && path.startsWith('/delete/')) {
      const key = path.replace('/delete/', '');
      await env.R2_BUCKET.delete(key);
      return new Response(JSON.stringify({ ok: true }), { headers: CORS });
    }

    return new Response(JSON.stringify({ ok:false, error:'Not found' }), { status:404, headers:CORS });
  }
};
