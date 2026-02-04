# Production Deployment Guide

This guide provides step-by-step instructions for deploying the Pi MR-NFT Agent to production.

## Prerequisites

1. **Pi Mainnet Access**
   - Pi Network RPC endpoint
   - Wallet with PI tokens for gas fees
   - Valid Ethereum-compatible address (0x...)

2. **Development Tools**
   - Python 3.11+
   - Docker (optional, for containerized deployment)
   - Git

## Deployment Options

### Option 1: Railway.app (Recommended)

Railway provides zero-config deployment with automatic SSL and monitoring.

1. **Sign up**: Visit [railway.app](https://railway.app) and create an account

2. **Create new project**: Click "New Project" → "Deploy from GitHub repo"

3. **Connect repository**: Authorize Railway to access your GitHub and select this repository

4. **Configure environment variables**:
   ```
   PI_NODE_RPC=https://api.node.pi.network
   PRIVATE_KEY=0x... (your wallet private key)
   CREATOR_ADDRESS=0x... (your Pi Mainnet address)
   CATALYST_POOL_ADDRESS=0x... (deployed contract address)
   MR_NFT_ADDRESS=0x... (deployed contract address)
   PORT=8000
   LOG_LEVEL=INFO
   ```

5. **Deploy**: Railway will automatically detect the `railway.json` config and deploy

6. **Verify**: Check the health endpoint at `https://your-app.railway.app/health`

### Option 2: Render.com

Render provides free-tier deployment with automatic SSL.

1. **Sign up**: Visit [render.com](https://render.com) and create an account

2. **Create Web Service**: Click "New" → "Web Service"

3. **Connect repository**: Connect your GitHub account and select this repository

4. **Configure**: Render will auto-detect the `render.yaml` file

5. **Add environment variables** (same as Railway above)

6. **Deploy**: Click "Create Web Service"

7. **Verify**: Check `https://your-app.onrender.com/health`

### Option 3: Heroku

1. **Install Heroku CLI**: 
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create app**:
   ```bash
   heroku create pi-mr-nft-agent
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set PI_NODE_RPC=https://api.node.pi.network
   heroku config:set PRIVATE_KEY=0x...
   heroku config:set CREATOR_ADDRESS=0x...
   heroku config:set CATALYST_POOL_ADDRESS=0x...
   heroku config:set MR_NFT_ADDRESS=0x...
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Verify**:
   ```bash
   heroku open /health
   ```

### Option 4: Docker Self-Hosted

For VPS or dedicated server deployment:

1. **Clone repository**:
   ```bash
   git clone https://github.com/onenoly1010/pi-mr-nft-agent.git
   cd pi-mr-nft-agent
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   nano .env
   ```

3. **Build and run**:
   ```bash
   docker-compose up -d
   ```

4. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Verify**:
   ```bash
   curl http://localhost:8000/health
   ```

## Contract Deployment

Before deploying the application, deploy the smart contracts:

### Manual Deployment with Forge

1. **Install Foundry**:
   ```bash
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

2. **Run deployment script**:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   bash scripts/deploy_pi_evm.sh
   ```

3. **Save contract addresses**: Copy the deployed addresses to your `.env` file

4. **Seed models** (optional):
   ```bash
   python scripts/seed_first_six_models.py
   ```

## Verification Checklist

After deployment, verify:

- [ ] Health endpoint returns `{"status": "ok"}` at `/health`
- [ ] Environment variables are properly configured
- [ ] Application logs show successful startup
- [ ] No error messages in deployment logs
- [ ] Contract addresses are valid and deployed
- [ ] RPC connection is working

## Monitoring

### Health Check

The application provides a health check endpoint:

```bash
curl https://your-app.com/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "pi-mr-nft-agent",
  "version": "1.0.0",
  "environment": {
    "rpc_configured": true,
    "creator_configured": true,
    "catalyst_pool_configured": true,
    "mr_nft_configured": true
  }
}
```

### Application Logs

Monitor application logs for errors:

**Railway**: View logs in the Railway dashboard
**Render**: View logs in the Render dashboard
**Heroku**: `heroku logs --tail`
**Docker**: `docker-compose logs -f`

## Troubleshooting

### Health Check Returns "degraded"

- Verify all required environment variables are set
- Check that addresses are valid Ethereum format (0x + 40 hex chars)
- Ensure RPC endpoint is accessible

### Application Won't Start

- Check deployment logs for Python errors
- Verify Python version is 3.11+
- Ensure all dependencies are installed
- Check for port conflicts (PORT=8000)

### Contract Deployment Fails

- Verify wallet has sufficient PI tokens for gas
- Check RPC endpoint is accessible
- Ensure private key is valid and has proper format
- Verify contract code compiles with `forge build`

## Security Best Practices

1. **Never commit secrets**: Keep `.env` out of version control
2. **Use environment variables**: Store all sensitive data as env vars
3. **Rotate keys regularly**: Change private keys periodically
4. **Monitor access**: Review deployment logs regularly
5. **Use HTTPS**: Always use SSL/TLS for production endpoints
6. **Limit exposure**: Don't expose unnecessary endpoints publicly

## Rollback Procedure

If deployment fails:

1. **Railway/Render**: Use the dashboard to rollback to previous deployment
2. **Heroku**: `heroku rollback`
3. **Docker**: `docker-compose down && git checkout <previous-commit> && docker-compose up -d`

## Support

For issues or questions:
- GitHub Issues: [github.com/onenoly1010/pi-mr-nft-agent/issues](https://github.com/onenoly1010/pi-mr-nft-agent/issues)
- See also: Main deployment documentation in repository root

---

**Remember**: Always test in staging/testnet before deploying to production!
