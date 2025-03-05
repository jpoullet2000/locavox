FROM postgres:15

# Set environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=postgres

# Set the timezone
ENV TZ=UTC

# Copy initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Expose the PostgreSQL port
EXPOSE 5432

# Add labels
LABEL maintainer="Locavox Team"
LABEL description="PostgreSQL database for Locavox application"
LABEL version="1.0"

# Set the default command
CMD ["postgres"]
