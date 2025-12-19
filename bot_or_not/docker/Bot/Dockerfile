# Build competitor bot image by extending the base
FROM emiliedu/bot_base:latest

# Example: allow teams to add dependencies
# RUN pip install --no-cache-dir <extra-dependency>
RUN pip install --no-cache-dir openai
RUN pip install --no-cache-dir numpy

COPY . .