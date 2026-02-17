# Supabase Storage Setup Guide

## Storage Buckets Required

Your app needs **3 storage buckets** in Supabase. Here's how to create and configure them:

---

## 1. Create Buckets

Go to: **Supabase Dashboard** → **Storage** → **Create bucket**

### Bucket 1: `cv-files`
- **Name:** `cv-files`
- **Public:** ✅ Yes (public bucket)
- **File size limit:** 50 MB
- **Allowed MIME types:** `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `text/plain`

### Bucket 2: `profile-photos`
- **Name:** `profile-photos`
- **Public:** ✅ Yes (public bucket)
- **File size limit:** 5 MB
- **Allowed MIME types:** `image/jpeg`, `image/png`, `image/jpg`

### Bucket 3: `training-letters`
- **Name:** `training-letters`
- **Public:** ❌ No (private bucket)
- **File size limit:** 10 MB
- **Allowed MIME types:** `application/pdf`, `text/plain`

---

## 2. Set RLS Policies

For each bucket, go to **Storage** → **Policies** → **New policy**

### Policies for `cv-files`

#### Policy 1: "Users can upload their own CV files"
```sql
-- INSERT policy
CREATE POLICY "Users can upload own CV files"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'cv-files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

#### Policy 2: "Users can read their own CV files"
```sql
-- SELECT policy
CREATE POLICY "Users can read own CV files"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'cv-files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

#### Policy 3: "Public can read CV files"
```sql
-- SELECT policy for public access
CREATE POLICY "Public can read CV files"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'cv-files');
```

---

### Policies for `profile-photos`

#### Policy 1: "Users can upload their own profile photo"
```sql
-- INSERT policy
CREATE POLICY "Users can upload own profile photo"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'profile-photos' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

#### Policy 2: "Users can update their own profile photo"
```sql
-- UPDATE policy
CREATE POLICY "Users can update own profile photo"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'profile-photos' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

#### Policy 3: "Public can read profile photos"
```sql
-- SELECT policy for public access
CREATE POLICY "Public can read profile photos"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'profile-photos');
```

---

### Policies for `training-letters`

#### Policy 1: "Users can upload their own training letter"
```sql
-- INSERT policy
CREATE POLICY "Users can upload own training letter"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'training-letters' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

#### Policy 2: "Users can read their own training letter"
```sql
-- SELECT policy (private - only owner can read)
CREATE POLICY "Users can read own training letter"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'training-letters' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

---

## 3. Verify Setup

Run this SQL query in Supabase SQL Editor to verify buckets exist:

```sql
SELECT
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types
FROM storage.buckets
WHERE name IN ('cv-files', 'profile-photos', 'training-letters')
ORDER BY name;
```

Expected output:
| id | name | public | file_size_limit | allowed_mime_types |
|----|------|--------|-----------------|-------------------|
| cv-files | cv-files | true | 52428800 | {application/pdf,...} |
| profile-photos | profile-photos | true | 5242880 | {image/jpeg,...} |
| training-letters | training-letters | false | 10485760 | {application/pdf,...} |

---

## 4. Test Upload

### Test CV Upload
```bash
curl -X POST https://platsbanken-ai.vercel.app/api/cv/upload-and-analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/cv.pdf"
```

### Test Profile Photo Upload
```bash
curl -X POST https://platsbanken-ai.vercel.app/api/upload/profile-photo \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/photo.jpg"
```

### Test Training Letter Upload
```bash
curl -X POST https://platsbanken-ai.vercel.app/api/upload/training-letter \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/letter.pdf"
```

---

## 5. Common Issues

### Error: "Kunde inte ladda upp CV"

**Cause:** Missing `user_cv_uploads` table

**Fix:** Run migration:
```
v2/supabase/migrations/fix_cv_upload_table.sql
```

---

### Error: "403 Forbidden" or "Row-level security policy"

**Cause:** Missing RLS policies on storage buckets

**Fix:**
1. Go to Storage → Policies
2. Add the policies listed in section 2 above
3. Make sure `bucket_id` matches exactly

---

### Error: "Bucket not found"

**Cause:** Storage bucket doesn't exist

**Fix:**
1. Go to Storage → Create bucket
2. Create the 3 buckets listed in section 1
3. Set correct public/private settings

---

### Error: "Invalid MIME type"

**Cause:** Trying to upload unsupported file format

**Fix:**
- CV uploads: Use PDF, DOCX, DOC, TXT, RTF, or ODT
- Photos: Use JPG or PNG
- Letters: Use PDF or TXT

---

## 6. Environment Variables

Make sure these are set in Vercel:

```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
ANTHROPIC_API_KEY=sk-ant-...
```

Without these, uploads will fail with authentication errors.

---

## Quick Checklist

- [ ] Created `cv-files` bucket (public)
- [ ] Created `profile-photos` bucket (public)
- [ ] Created `training-letters` bucket (private)
- [ ] Added RLS policies for `cv-files`
- [ ] Added RLS policies for `profile-photos`
- [ ] Added RLS policies for `training-letters`
- [ ] Ran `fix_cv_upload_table.sql` migration
- [ ] Verified environment variables in Vercel
- [ ] Tested upload in deployed app

---

## Need Help?

Check Supabase logs:
```
Supabase Dashboard → Logs → Realtime
```

Check API logs:
```
Vercel Dashboard → Deployments → [Latest] → Logs
```
