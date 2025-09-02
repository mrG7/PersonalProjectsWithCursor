#!/usr/bin/env python3
"""
Cursor Super Prompt Agent Setup Script

This script helps you set up and configure AI agents based on the Cursor Super Prompt templates.
It creates the necessary directory structure, configuration files, and initial setup for your agents.

Usage:
    python setup_agent.py [agent_type]

Available agent types:
    - gig_finder
    - content_creator
    - market_research
    - custom (for custom agent setup)
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class AgentSetup:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.templates_dir = self.base_dir / "templates"
        self.examples_dir = self.base_dir / "examples"

    def create_directories(self, agent_name):
        """Create the necessary directory structure for the agent."""
        agent_dir = self.base_dir / "my_agents" / agent_name
        subdirs = ["config", "logs", "output", "data", "scripts"]

        for subdir in subdirs:
            (agent_dir / subdir).mkdir(parents=True, exist_ok=True)

        print(f"✅ Created directory structure for agent: {agent_name}")
        return agent_dir

    def copy_template(self, agent_type, agent_name):
        """Copy the appropriate template based on agent type."""
        template_map = {
            "gig_finder": "examples/gig_finder_agent.prompt",
            "content_creator": "examples/content_creator.prompt",
            "market_research": "examples/market_research.prompt",
            "custom": "templates/agent_base.template"
        }

        if agent_type not in template_map:
            print(f"❌ Unknown agent type: {agent_type}")
            return False

        source = self.base_dir / template_map[agent_type]
        if not source.exists():
            print(f"❌ Template not found: {source}")
            return False

        agent_dir = self.create_directories(agent_name)
        destination = agent_dir / f"{agent_name}.prompt"

        shutil.copy2(source, destination)
        print(f"✅ Copied template to: {destination}")
        return True

    def create_config_file(self, agent_name, agent_type):
        """Create a configuration file for the agent."""
        agent_dir = self.base_dir / "my_agents" / agent_name
        config_file = agent_dir / "config" / "agent_config.json"

        config = {
            "agent_name": agent_name,
            "agent_type": agent_type,
            "created_date": datetime.now().isoformat(),
            "version": "1.0.0",
            "settings": {
                "log_level": "INFO",
                "max_runtime": "2h",
                "retry_attempts": 3,
                "notification_enabled": True,
                "auto_backup": True
            },
            "schedule": {
                "frequency": "daily",
                "preferred_time": "09:00",
                "timezone": "UTC"
            },
            "paths": {
                "base_dir": str(agent_dir),
                "logs_dir": str(agent_dir / "logs"),
                "output_dir": str(agent_dir / "output"),
                "data_dir": str(agent_dir / "data"),
                "config_dir": str(agent_dir / "config")
            },
            "integrations": {
                "email_enabled": False,
                "api_access": [],
                "external_tools": []
            }
        }

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Created configuration file: {config_file}")
        return config_file

    def create_log_file(self, agent_name):
        """Create initial log file for the agent."""
        agent_dir = self.base_dir / "my_agents" / agent_name
        log_file = agent_dir / "logs" / "agent.log"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_log = f"[{timestamp}] Agent '{agent_name}' initialized successfully\n"
        initial_log += f"[{timestamp}] Log file created at: {log_file}\n"
        initial_log += f"[{timestamp}] Agent ready for operation\n"

        with open(log_file, 'w') as f:
            f.write(initial_log)

        print(f"✅ Created log file: {log_file}")
        return log_file

    def create_readme(self, agent_name, agent_type):
        """Create a README file with setup instructions."""
        agent_dir = self.base_dir / "my_agents" / agent_name
        readme_file = agent_dir / "README.md"

        readme_content = f"""# {agent_name} Agent

## Overview
This agent was created using the Cursor Super Prompt template system.
- **Type:** {agent_type}
- **Created:** {datetime.now().strftime("%Y-%m-%d")}
- **Template:** Based on Cursor Super Prompt v1.0

## Directory Structure
```
{agent_name}/
├── config/
│   └── agent_config.json    # Agent configuration settings
├── logs/
│   └── agent.log           # Operation logs
├── output/                 # Generated outputs and reports
├── data/                   # Data files and resources
├── scripts/               # Custom scripts and automation
├── {agent_name}.prompt     # Main agent prompt
└── README.md              # This file
```

## Quick Start

1. **Review Configuration**
   - Edit `config/agent_config.json` to customize settings
   - Adjust schedule, notifications, and integrations

2. **Customize Agent**
   - Modify `{agent_name}.prompt` for your specific needs
   - Add custom instructions and parameters

3. **Set Up Automation**
   - Configure scheduling (cron/Windows Task Scheduler)
   - Set up notification preferences
   - Test the agent manually first

4. **Monitor Operation**
   - Check `logs/agent.log` for activity
   - Review outputs in the `output/` directory
   - Adjust configuration based on performance

## Configuration Options

### Basic Settings
- `log_level`: INFO, DEBUG, WARNING, ERROR
- `max_runtime`: Maximum execution time
- `retry_attempts`: Number of retry attempts on failure
- `notification_enabled`: Enable/disable notifications

### Scheduling
- `frequency`: daily, weekly, hourly
- `preferred_time`: Time to run (HH:MM format)
- `timezone`: Timezone for scheduling

## Customization

### Adding New Capabilities
1. Edit the main prompt file
2. Add new sections for specific tasks
3. Update configuration if needed
4. Test changes thoroughly

### Integration Setup
1. Enable integrations in config
2. Add API keys and credentials
3. Configure external service connections
4. Test integration endpoints

## Troubleshooting

### Common Issues
- **Agent not running**: Check log files for errors
- **Configuration errors**: Validate JSON syntax
- **Permission issues**: Ensure proper file permissions
- **Integration failures**: Verify API credentials

### Getting Help
- Check the main Cursor Super Prompt documentation
- Review example configurations
- Consult the troubleshooting guide

## Maintenance

### Regular Tasks
- [ ] Review log files weekly
- [ ] Update configuration as needed
- [ ] Backup important data
- [ ] Monitor performance metrics

### Updates
- [ ] Check for template updates
- [ ] Review new features and capabilities
- [ ] Update agent configuration
- [ ] Test updated functionality

---

*Generated by Cursor Super Prompt Agent Setup Script*
"""

        with open(readme_file, 'w') as f:
            f.write(readme_content)

        print(f"✅ Created README file: {readme_file}")
        return readme_file

    def setup_agent(self, agent_type, agent_name=None):
        """Main setup function for creating a new agent."""
        if agent_name is None:
            agent_name = f"{agent_type}_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"🚀 Setting up {agent_type} agent: {agent_name}")
        print("=" * 50)

        # Create directories
        agent_dir = self.create_directories(agent_name)

        # Copy template
        if not self.copy_template(agent_type, agent_name):
            return False

        # Create configuration
        self.create_config_file(agent_name, agent_type)

        # Create log file
        self.create_log_file(agent_name)

        # Create README
        self.create_readme(agent_name, agent_type)

        print("=" * 50)
        print(f"✅ Agent setup complete!")
        print(f"📁 Agent directory: {agent_dir}")
        print(f"📝 Main prompt: {agent_dir}/{agent_name}.prompt")
        print(f"⚙️  Configuration: {agent_dir}/config/agent_config.json")
        print()
        print("Next steps:")
        print("1. Review and customize the agent prompt")
        print("2. Update configuration settings")
        print("3. Test the agent manually")
        print("4. Set up automation scheduling")
        print()
        print("Happy automating! 🤖")

        return True

def main():
    """Main function to handle command line arguments."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python setup_agent.py [agent_type] [agent_name]")
        print()
        print("Available agent types:")
        print("  - gig_finder")
        print("  - content_creator")
        print("  - market_research")
        print("  - custom")
        print()
        print("Example:")
        print("  python setup_agent.py gig_finder my_gig_agent")
        return

    agent_type = sys.argv[1].lower()
    agent_name = sys.argv[2] if len(sys.argv) > 2 else None

    valid_types = ["gig_finder", "content_creator", "market_research", "custom"]

    if agent_type not in valid_types:
        print(f"❌ Invalid agent type: {agent_type}")
        print(f"Valid types: {', '.join(valid_types)}")
        return

    setup = AgentSetup()
    setup.setup_agent(agent_type, agent_name)

if __name__ == "__main__":
    main()
