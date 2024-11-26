-- Allow authenticated users to upload their own CV
CREATE POLICY "Users can upload their own CV"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (
  bucket_id = 'documents' AND
  (storage.foldername(name))[1] = 'cv' AND
  auth.uid()::text = (storage.foldername(name))[2]
);

-- Allow users to read their own CV
CREATE POLICY "Users can read their own CV"
ON storage.objects FOR SELECT TO authenticated
USING (
  bucket_id = 'documents' AND
  (storage.foldername(name))[1] = 'cv' AND
  auth.uid()::text = (storage.foldername(name))[2]
);

-- Allow service role full access
CREATE POLICY "Service role has full access to documents"
ON storage.objects FOR ALL TO service_role USING (bucket_id = 'documents');
