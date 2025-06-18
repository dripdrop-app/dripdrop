from fastapi import status

from app.music.tests.test_base import MusicBaseTest

CREATE_URL = "/api/music/job/create"
DELETE_URL = "/api/music/job/{job_id}/delete"


class DeleteMusicJobTestCase(MusicBaseTest):
    async def test_deleting_job_when_not_logged_in(self):
        response = await self.client.delete(DELETE_URL.format(job_id=1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_deleting_nonexistent_job(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.delete(DELETE_URL.format(job_id=1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_deleting_failed_job(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        job = await self.create_music_job(
            id="1",
            email=user.email,
            title="title",
            artist="artist",
            album="album",
            failed=True,
        )
        response = await self.client.delete(DELETE_URL.format(job_id=job.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_deleting_job_with_cleanup(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
            },
            files={
                "file": ("tun suh.mp3", MusicBaseTest.test_audio_file, "audio/mpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertTrue(job.completed)
        response = await self.client.delete(DELETE_URL.format(job_id=job.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = await self.http_client.get(job.filename_url)
        self.assertIn(
            response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]
        )
        response = await self.http_client.get(job.download_url)
        self.assertIn(
            response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]
        )
