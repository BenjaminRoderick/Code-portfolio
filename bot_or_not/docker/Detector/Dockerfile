# Build competitor detector image by extending the base
FROM emiliedu/detector_base:latest

# Example: allow teams to add dependencies
# RUN pip install --no-cache-dir <extra-dependency>
RUN pip install --no-cache-dir transformers
RUN pip install --no-cache-dir torch
RUN pip install --no-cache-dir emoji

COPY . .