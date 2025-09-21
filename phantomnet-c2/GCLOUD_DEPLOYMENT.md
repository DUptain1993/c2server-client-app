# PhantomNet C2 Server - Google Cloud Deployment Guide

## Overview
This guide covers deploying the containerized PhantomNet C2 server to Google Cloud Platform using various deployment options.

## Prerequisites
- Google Cloud SDK installed and configured
- Docker installed locally
- Valid SSL certificates (Let's Encrypt recommended for production)
- Domain name configured (optional but recommended)

## Deployment Options

### Option 1: Google Cloud Run (Recommended for Simplicity)

#### 1. Build and Push to Container Registry
```bash
# Tag the image for Google Container Registry
docker tag phantomnet-c2:latest gcr.io/YOUR_PROJECT_ID/phantomnet-c2:latest

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/phantomnet-c2:latest
```

#### 2. Deploy to Cloud Run
```bash
gcloud run deploy phantomnet-c2 \
    --image gcr.io/YOUR_PROJECT_ID/phantomnet-c2:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8443 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 3 \
    --set-env-vars="FLASK_ENV=production,DEBUG=false,LOG_LEVEL=INFO"
```

#### 3. Configure Custom Domain (Optional)
```bash
gcloud run domain-mappings create \
    --service phantomnet-c2 \
    --domain your-domain.com \
    --region us-central1
```

### Option 2: Google Kubernetes Engine (GKE)

#### 1. Create GKE Cluster
```bash
gcloud container clusters create phantomnet-cluster \
    --zone us-central1-a \
    --num-nodes 2 \
    --machine-type e2-medium \
    --enable-autorepair \
    --enable-autoupgrade
```

#### 2. Create Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phantomnet-c2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: phantomnet-c2
  template:
    metadata:
      labels:
        app: phantomnet-c2
    spec:
      containers:
      - name: phantomnet-c2
        image: gcr.io/YOUR_PROJECT_ID/phantomnet-c2:latest
        ports:
        - containerPort: 8443
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DEBUG
          value: "false"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: ssl-certs
          mountPath: /certs
          readOnly: true
      volumes:
      - name: ssl-certs
        secret:
          secretName: ssl-certificates
---
apiVersion: v1
kind: Service
metadata:
  name: phantomnet-c2-service
spec:
  selector:
    app: phantomnet-c2
  ports:
  - port: 443
    targetPort: 8443
    protocol: TCP
  type: LoadBalancer
```

#### 3. Deploy to GKE
```bash
kubectl apply -f k8s-deployment.yaml
```

### Option 3: Compute Engine VM

#### 1. Create VM Instance
```bash
gcloud compute instances create phantomnet-vm \
    --zone us-central1-a \
    --machine-type e2-medium \
    --boot-disk-size 20GB \
    --image-family ubuntu-2004-lts \
    --image-project ubuntu-os-cloud \
    --tags http-server,https-server
```

#### 2. Configure Firewall Rules
```bash
gcloud compute firewall-rules create allow-phantomnet \
    --allow tcp:8443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow PhantomNet C2 traffic"
```

#### 3. Deploy via SSH
```bash
# SSH to the VM
gcloud compute ssh phantomnet-vm --zone us-central1-a

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

# Transfer and run the container
# (Upload your docker-compose.yml and certificates)
docker-compose up -d
```

## Security Considerations

### 1. SSL/TLS Configuration
- **Production**: Use Let's Encrypt or commercial SSL certificates
- **Testing**: Self-signed certificates (as created in setup)
- Mount certificates as secrets in Kubernetes or secure volumes

### 2. Network Security
```bash
# Restrict access to specific IP ranges
gcloud compute firewall-rules create phantomnet-restricted \
    --allow tcp:8443 \
    --source-ranges YOUR_IP_RANGE/32 \
    --target-tags phantomnet-server
```

### 3. Environment Variables
Create a `.env` file for production:
```bash
# Production environment variables
FLASK_ENV=production
DEBUG=false
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:pass@host/db  # For production DB
SSL_CERT_PATH=/certs/fullchain.pem
SSL_KEY_PATH=/certs/privkey.pem
LOG_LEVEL=WARNING
SESSION_TIMEOUT=3600
RATE_LIMIT_ENABLED=true
MAX_LOGIN_ATTEMPTS=3
LOCKOUT_DURATION=1800
```

### 4. Database Configuration
For production, consider using:
- **Cloud SQL** (PostgreSQL/MySQL)
- **Cloud Firestore** (NoSQL)
- **Cloud Spanner** (Global scale)

Example Cloud SQL connection:
```bash
# Create Cloud SQL instance
gcloud sql instances create phantomnet-db \
    --database-version POSTGRES_13 \
    --tier db-f1-micro \
    --region us-central1
```

## Monitoring and Logging

### 1. Cloud Logging
```bash
# View logs in Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=phantomnet-c2"
```

### 2. Cloud Monitoring
Set up alerts for:
- High CPU/Memory usage
- Error rates
- Response times
- Failed authentication attempts

### 3. Health Checks
The container includes a health check endpoint at `/health`

## Cost Optimization

### Cloud Run Pricing (Recommended)
- **CPU**: $0.000024 per vCPU-second
- **Memory**: $0.0000025 per GiB-second
- **Requests**: $0.40 per million requests
- **Estimated monthly cost**: $5-15 for light usage

### GKE Pricing
- **Cluster management**: $0.10 per hour
- **Node costs**: Based on Compute Engine pricing
- **Estimated monthly cost**: $50-100+ depending on usage

### Compute Engine Pricing
- **e2-medium**: ~$25/month
- **Additional costs**: Storage, network egress

## Backup and Disaster Recovery

### 1. Database Backups
```bash
# Automated backups for Cloud SQL
gcloud sql backups create --instance phantomnet-db
```

### 2. Container Registry Backups
Images in GCR are automatically replicated across regions.

### 3. Configuration Backups
Store all configuration files in a private Git repository.

## Scaling Considerations

### Horizontal Scaling
- **Cloud Run**: Automatic scaling (0-1000 instances)
- **GKE**: Configure HPA (Horizontal Pod Autoscaler)
- **Compute Engine**: Use managed instance groups

### Vertical Scaling
- Adjust memory/CPU limits based on usage patterns
- Monitor resource utilization and adjust accordingly

## Troubleshooting

### Common Issues
1. **SSL Certificate Errors**: Ensure certificates are properly mounted and readable
2. **Database Connection**: Check network connectivity and credentials
3. **Memory Issues**: Increase memory limits if experiencing OOM kills
4. **Permission Errors**: Verify container runs as non-root user

### Debug Commands
```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision"

# GKE pod logs
kubectl logs -f deployment/phantomnet-c2

# Container debugging
docker exec -it phantomnet-c2 /bin/bash
```

## Security Hardening Checklist

- [ ] Use production SSL certificates
- [ ] Configure firewall rules to restrict access
- [ ] Enable audit logging
- [ ] Set up monitoring and alerting
- [ ] Use secrets management for sensitive data
- [ ] Regular security updates and patches
- [ ] Network segmentation (VPC)
- [ ] Identity and Access Management (IAM) roles
- [ ] Enable Cloud Security Command Center
- [ ] Regular penetration testing

## Next Steps

1. **Choose deployment method** based on your requirements
2. **Set up monitoring** and alerting
3. **Configure production database**
4. **Implement CI/CD pipeline** for automated deployments
5. **Set up backup and disaster recovery**
6. **Perform security audit** and penetration testing

---

**Note**: This is a C2 (Command and Control) server for security research and authorized penetration testing only. Ensure compliance with all applicable laws and regulations in your jurisdiction.