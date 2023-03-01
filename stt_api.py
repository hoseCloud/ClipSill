from google.cloud import speech

def transcribe_gcs(gcs_uri, tmp_file_name, conn):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=16000,
        language_code="ko-KR",
        #max_alternatives=3,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    conn.sendall("[4/10] Waiting For Operation...".encode())
    response = operation.result(timeout=300)

    f = open(tmp_file_name, "w")

    conn.sendall("[5/10] Waiting For Transcription...".encode())
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        f.write(result.alternatives[0].transcript + "\n")
        #print(u"Transcript: {}".format(result.alternatives[0].transcript))
        #print("Confidence: {}".format(result.alternatives[0].confidence))

    f.close()
