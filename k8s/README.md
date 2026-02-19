# JisCA_NOp - Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Nginx Ingress Controller installed
- cert-manager (optional, for TLS)

## Quick Deploy

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n jisca-nop
kubectl get svc -n jisca-nop
```

## Step-by-Step Deployment

### 1. Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Create ConfigMap and Secrets
**Important**: Update secrets before deploying!

```bash
# Edit secrets
vim k8s/configmap.yaml

# Apply
kubectl apply -f k8s/configmap.yaml
```

### 3. Deploy MongoDB
```bash
kubectl apply -f k8s/mongodb.yaml

# Wait for MongoDB to be ready
kubectl wait --for=condition=ready pod -l app=mongodb -n jisca-nop --timeout=300s
```

### 4. Create Persistent Volume Claims
```bash
kubectl apply -f k8s/pvc.yaml
```

### 5. Deploy Backend
```bash
# Build and push Docker image
docker build -t your-registry/jisca-nop-backend:latest ./backend
docker push your-registry/jisca-nop-backend:latest

# Update image in k8s/backend.yaml
# Then apply
kubectl apply -f k8s/backend.yaml
```

### 6. Deploy Frontend
```bash
# Build and push Docker image
docker build -t your-registry/jisca-nop-frontend:latest ./frontend
docker push your-registry/jisca-nop-frontend:latest

# Update image in k8s/frontend.yaml
# Then apply
kubectl apply -f k8s/frontend.yaml
```

### 7. Setup Ingress
```bash
# Update domain in k8s/ingress.yaml
vim k8s/ingress.yaml

# Apply
kubectl apply -f k8s/ingress.yaml
```

### 8. Enable Auto-scaling (Optional)
```bash
kubectl apply -f k8s/hpa.yaml
```

## Monitoring

```bash
# Check pods
kubectl get pods -n jisca-nop -w

# Check logs
kubectl logs -f deployment/backend -n jisca-nop
kubectl logs -f deployment/frontend -n jisca-nop

# Check services
kubectl get svc -n jisca-nop

# Check ingress
kubectl get ingress -n jisca-nop
```

## Scaling

```bash
# Manual scaling
kubectl scale deployment backend --replicas=5 -n jisca-nop
kubectl scale deployment frontend --replicas=3 -n jisca-nop

# Check HPA status
kubectl get hpa -n jisca-nop
```

## Updating

```bash
# Update backend
docker build -t your-registry/jisca-nop-backend:v2 ./backend
docker push your-registry/jisca-nop-backend:v2
kubectl set image deployment/backend backend=your-registry/jisca-nop-backend:v2 -n jisca-nop

# Update frontend
docker build -t your-registry/jisca-nop-frontend:v2 ./frontend
docker push your-registry/jisca-nop-frontend:v2
kubectl set image deployment/frontend frontend=your-registry/jisca-nop-frontend:v2 -n jisca-nop

# Check rollout status
kubectl rollout status deployment/backend -n jisca-nop
kubectl rollout status deployment/frontend -n jisca-nop
```

## Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n jisca-nop
kubectl rollout undo deployment/frontend -n jisca-nop

# Rollback to specific revision
kubectl rollout history deployment/backend -n jisca-nop
kubectl rollout undo deployment/backend --to-revision=2 -n jisca-nop
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace jisca-nop

# Or delete individually
kubectl delete -f k8s/
```

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod <pod-name> -n jisca-nop
kubectl logs <pod-name> -n jisca-nop
```

### Service not accessible
```bash
kubectl get endpoints -n jisca-nop
kubectl describe service backend -n jisca-nop
```

### Persistent storage issues
```bash
kubectl get pvc -n jisca-nop
kubectl describe pvc uploads-pvc -n jisca-nop
```

## Production Considerations

1. **Secrets Management**: Use external secret managers (Vault, AWS Secrets Manager)
2. **Resource Limits**: Adjust CPU/memory based on load testing
3. **Monitoring**: Deploy Prometheus + Grafana for monitoring
4. **Logging**: Use EFK stack (Elasticsearch, Fluentd, Kibana)
5. **Backup**: Regular MongoDB backups
6. **TLS**: Configure cert-manager for automatic SSL certificates
7. **Network Policies**: Implement network policies for security
8. **RBAC**: Configure proper role-based access control
