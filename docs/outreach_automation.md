# Outreach Automation

This document describes the outreach automation system for ARCO, which is used to send personalized outreach messages to qualified prospects.

## Overview

The outreach automation system integrates with the enrichment pipeline to automatically send personalized outreach messages to qualified prospects. It uses the progress tracker to identify qualified prospects and sends personalized messages based on the prospect's ICP and financial leak analysis.

## Components

### Outreach Integration

The outreach integration provides a common interface for sending messages through different channels. Currently, the following integrations are supported:

- **Email Outreach**: Sends personalized emails to prospects using SMTP.

### Outreach Manager

The outreach manager is a singleton that manages outreach integrations and provides a high-level API for sending messages. It also handles template selection based on prospect analysis.

### Templates

Templates are used to create personalized messages for prospects. Each template has a name, subject, and body, and can include personalization variables that are replaced with prospect-specific values.

The following templates are available by default:

- **shopify_dtc_initial**: Initial outreach template for Shopify DTC Premium ICP
- **health_supplements_initial**: Initial outreach template for Health Supplements ICP
- **fitness_equipment_initial**: Initial outreach template for Fitness Equipment ICP
- **high_roi_initial**: Generic template for prospects with high ROI
- **follow_up_template**: Follow-up template for prospects who haven't responded

### Personalization

Templates can include personalization variables that are replaced with prospect-specific values. The following variables are available:

- **first_name**: Prospect's first name
- **last_name**: Prospect's last name
- **full_name**: Prospect's full name
- **company_name**: Prospect's company name
- **domain**: Prospect's domain
- **website**: Prospect's website
- **position**: Prospect's position
- **date**: Current date
- **sender_name**: Sender's name
- **monthly_waste**: Monthly waste amount
- **annual_waste**: Annual waste amount
- **monthly_savings**: Monthly savings amount
- **annual_savings**: Annual savings amount
- **roi_percentage**: ROI percentage
- **top_recommendation**: Top recommendation

## Usage

### Sending Initial Outreach

To send initial outreach to qualified prospects:

```python
from arco.integrations.outreach_integration import outreach_manager
from arco.models.prospect import Prospect

# Initialize outreach integration
outreach_manager.initialize_integration(
    "email",
    smtp_server="smtp.example.com",
    smtp_port=587,
    username="user",
    password="pass",
    from_email="from@example.com",
    from_name="ARCO Team"
)

# Send initial outreach
message_id = outreach_manager.send_message(
    prospect=prospect,
    template_name="shopify_dtc_initial",
    personalization={
        "monthly_waste": "$500.00",
        "annual_waste": "$6,000.00",
        "monthly_savings": "$400.00",
        "annual_savings": "$4,800.00",
        "roi_percentage": "25.0%",
        "top_recommendation": "Consolidate analytics tools"
    }
)
```

### Sending Follow-up Outreach

To send follow-up outreach to prospects who haven't responded:

```python
from arco.integrations.outreach_integration import outreach_manager
from arco.models.prospect import Prospect

# Send follow-up outreach
message_id = outreach_manager.send_follow_up(
    prospect=prospect,
    days_since_contact=3
)
```

### Creating Custom Templates

To create custom templates:

```python
from arco.integrations.outreach_integration import outreach_manager

# Create a custom template
template_id = outreach_manager.create_template(
    name="custom_template",
    subject="Custom Subject for {{company_name}}",
    body="""
    <p>Hi {{first_name}},</p>

    <p>This is a custom template for {{company_name}}.</p>

    <p>Best regards,<br>
    {{sender_name}}</p>
    """
)
```

## Integration with Enrichment Pipeline

The outreach automation system integrates with the enrichment pipeline to automatically send outreach messages to qualified prospects. The integration is implemented in the `apollo_pipeline_with_outreach.py` example.

To run the integrated pipeline:

```bash
python examples/apollo_pipeline_with_outreach.py --limit 20 --batch-size 5 --auto-outreach --follow-up-days 3
```

## Standalone Outreach Automation

The outreach automation system can also be run standalone to send outreach messages to previously qualified prospects. This is implemented in the `apollo_outreach_automation.py` example.

To run the standalone outreach automation:

```bash
python examples/apollo_outreach_automation.py --qualified-only --days-since-contact 3
```

## Progress Tracking

The outreach automation system integrates with the progress tracker to track the status of outreach messages. The following stages are used:

- **CONTACTED**: Prospect has been sent an initial outreach message
- **ENGAGED**: Prospect has responded to an outreach message

## Metrics

The outreach automation system tracks the following metrics:

- **Contact Rate**: Percentage of qualified prospects that have been contacted
- **Engagement Rate**: Percentage of contacted prospects that have engaged
- **Success Rate**: Percentage of outreach messages that were successfully sent
