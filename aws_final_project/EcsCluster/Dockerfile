FROM swaggerapi/swagger-ui:latest
ENV PORT=80
COPY ./swagger.json /app/
CMD ["nginx", "-g", "daemon off;"]
EXPOSE 80