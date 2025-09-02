# Troubleshooting Guide - Cursor Super Prompt

This guide helps you diagnose and resolve common issues with Cursor Super Prompt agents and templates.

## 🔍 Quick Diagnosis

### Agent Not Starting
**Symptoms:** Agent fails to execute or initialize
```
✅ Check these first:
1. Verify Python/Node.js installation
2. Check file permissions on agent directory
3. Review agent configuration file syntax
4. Confirm all required dependencies are installed
5. Check system PATH environment variable
```

**Common Solutions:**
- Run `python --version` or `node --version` to verify installation
- Use `chmod +x script.py` to make scripts executable
- Validate JSON/YAML syntax with online validators
- Install missing packages with `pip install` or `npm install`

### Configuration Errors
**Symptoms:** Agent loads but behaves unexpectedly
```
🔧 Configuration Validation:
1. Check YAML/JSON syntax
2. Verify file paths exist
3. Confirm API keys are valid
4. Validate schedule format
5. Check integration settings
```

**Validation Commands:**
```bash
# YAML syntax check
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# JSON syntax check
python -c "import json; json.load(open('config.json'))"

# Path existence check
ls -la /path/to/check
```

### Performance Issues
**Symptoms:** Agent runs slowly or consumes excessive resources
```
⚡ Performance Optimization:
1. Reduce batch processing size
2. Implement caching mechanisms
3. Optimize database queries
4. Reduce logging verbosity
5. Check memory usage patterns
```

## 🚨 Common Error Messages

### "Module Not Found" Errors
```
Error: Module 'requests' not found

Solution:
pip install requests
# or for specific versions
pip install requests==2.28.0
```

### "Permission Denied" Errors
```
Error: Permission denied: 'output.txt'

Solution:
# Check current permissions
ls -la output.txt

# Fix permissions
chmod 644 output.txt
# or for directories
chmod 755 output_directory/
```

### "Connection Timeout" Errors
```
Error: Connection to api.example.com timed out

Solution:
1. Check internet connectivity
2. Verify API endpoint URL
3. Increase timeout settings
4. Check firewall/proxy settings
5. Verify API key authentication
```

### "Memory Error" Issues
```
Error: MemoryError: Unable to allocate memory

Solution:
1. Reduce batch processing size
2. Implement streaming for large files
3. Increase system memory limits
4. Optimize data structures
5. Use memory profiling tools
```

## 🔧 Agent-Specific Troubleshooting

### Gig Finder Agent Issues

**No Opportunities Found:**
- Check search keywords and filters
- Verify platform access and credentials
- Review rate limiting and API quotas
- Update search criteria for current market

**Poor Quality Matches:**
- Refine qualification criteria
- Update skill keywords
- Adjust budget ranges
- Review client rating filters

### Content Creator Agent Issues

**Content Generation Errors:**
- Check API rate limits
- Verify content guidelines
- Review prompt specificity
- Update content templates

**Publishing Failures:**
- Verify platform credentials
- Check API permissions
- Review content formatting
- Confirm posting limits

### Market Research Agent Issues

**Data Collection Failures:**
- Verify data source accessibility
- Check API authentication
- Review scraping permissions
- Update data source URLs

**Analysis Errors:**
- Validate data formats
- Check statistical assumptions
- Review sample sizes
- Verify calculation methods

## 🛠️ Advanced Debugging

### Enable Debug Logging
```python
# In your agent configuration
logging:
  level: DEBUG
  file: debug.log
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### Memory Profiling
```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Your code here
# ...

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

### Performance Monitoring
```python
import time
import psutil

start_time = time.time()
start_memory = psutil.Process().memory_info().rss

# Your operation here
# ...

end_time = time.time()
end_memory = psutil.Process().memory_info().rss

print(f"Execution time: {end_time - start_time:.2f} seconds")
print(f"Memory used: {(end_memory - start_memory) / 1024 / 1024:.1f} MB")
```

## 🔄 System Recovery

### Agent Recovery Steps
1. **Stop the agent** safely
2. **Backup current state** and logs
3. **Reset configuration** to defaults
4. **Clear cache/temp files**
5. **Restart with minimal settings**
6. **Gradually restore features**

### Data Recovery
```bash
# Create backup before recovery
cp -r agent_data agent_data_backup

# Clear corrupted data
rm -rf agent_data/cache/*
rm -rf agent_data/temp/*

# Restore from backup if needed
cp -r agent_data_backup/* agent_data/
```

### Configuration Reset
```bash
# Backup current config
cp config.yaml config.yaml.backup

# Reset to template
cp templates/config_template.yaml config.yaml

# Edit with minimal required settings
nano config.yaml
```

## 📞 Getting Help

### Self-Help Resources
1. **Check Logs First**
   ```
   tail -f logs/agent.log
   grep "ERROR" logs/agent.log
   ```

2. **Review Documentation**
   - Main README.md
   - Agent-specific documentation
   - API documentation for integrations

3. **Test Incrementally**
   - Start with basic functionality
   - Add features one at a time
   - Test after each change

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share solutions
- **Documentation**: Contribute improvements

### Professional Support
- **Consulting**: Hire experts for complex issues
- **Training**: Learn advanced agent development
- **Custom Development**: Build specialized solutions

## 🚀 Preventive Maintenance

### Regular Tasks
- [ ] Update dependencies monthly
- [ ] Review and rotate API keys quarterly
- [ ] Backup configurations weekly
- [ ] Monitor performance metrics
- [ ] Update documentation

### Health Checks
```bash
# System health check
python -c "import sys; print('Python version:', sys.version)"

# Dependency check
pip list --outdated

# Disk space check
df -h

# Memory check
free -h
```

### Performance Benchmarks
- Track execution times
- Monitor memory usage
- Log error rates
- Measure success rates
- Compare against baselines

---

## 📋 Emergency Checklist

When everything goes wrong:
1. [ ] Stop all agent processes
2. [ ] Create full system backup
3. [ ] Document current state
4. [ ] Isolate the problem
5. [ ] Start with minimal configuration
6. [ ] Test basic functionality
7. [ ] Gradually restore features
8. [ ] Update monitoring and alerts

Remember: Most issues have simple solutions. Start with the basics and work systematically through the problem.
