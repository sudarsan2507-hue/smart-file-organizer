from core.pipeline import ProcessingPipeline

pipeline = ProcessingPipeline(".")

category = pipeline.process_file("test.txt")

print("Final Category:", category)