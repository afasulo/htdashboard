# HitTrax Baseball Analytics Dashboard

A comprehensive baseball analytics dashboard built with Python and Dash, designed to visualize and analyze HitTrax data. The dashboard provides detailed player statistics, performance trends, and leaderboards for baseball players.
<img width="1673" alt="image" src="https://github.com/user-attachments/assets/19409a09-aee2-499a-8ae4-a8e0b54166b2" />

<img width="670" alt="image" src="https://github.com/user-attachments/assets/90f0b435-a335-4f78-9c3e-fa79396a68e5" />


## Future improvements/fixes
- fix export to social media button. export to social media should copy the pdf to a sqaure nxn image
- calculate grad year in a better way. Might be able to automatically calcualte this and update the SQLite DB? may have to update manually
- fix hittrax analysis tab. when you click on a players name in table, it does not open up summary and dbo.sessions table correctly. It opens it for the wrong athlete. If you click on John Doe, you get Jane Smith, etc.....
- work on adding a custom image header. Ex. /assets/pdf_header.pdf was my attempt at that but cant get margins or format correct
- add support for overlaying data and player cards onto a image, aka an pretty background.


# Dev Notes for adam
### decode Users.SkilllLevel
- 0 => 12u 
- 1 => 15u
- 2 => High School
- 3 => College
- 4 => Professional
- 5 => 13u
- 6 => 10u
- 7 =>  8u

Pretty intuitive right?...

### decode Users.active (active/archived)
- 1 => active 
- 0 => archived

I would like to test/discover if deleting users from users table would break anything. I guess theey would be left with dangling rows in the sessions and plays table. No valid userID to reference back to. Need to think about a safe user delete util someday


## Features

- **Player Analytics**
  - Exit velocity and distance scatter plots
  - Batting statistics radar charts
  - Performance trend analysis
  - Detailed session-by-session breakdowns

- **Leaderboards**
  - Exit velocity rankings (max and average)
  - Distance rankings (max and average)
  - Graduation year filtering
  - School-based comparisons

- **Interactive Data Filtering**
  - Skill level filtering
  - Player selection
  - Minimum at-bats threshold
  - Date range selection

- **Data Visualization**
  - Heat maps for hit distribution
  - Box plots for statistical analysis
  - Time series charts for performance tracking
  - Interactive tables with sorting and filtering

## Technical Stack

- **Frontend**: Dash, Plotly
- **Backend**: Python
- **Database**: 
  - Primary: Microsoft SQL Server (HitTrax)
  - Local: SQLite (for caching and performance)
- **Key Libraries**:
  - `dash==2.14.2`
  - `plotly==5.18.0`
  - `pandas==2.1.4`
  - `numpy==1.26.2`
  - `pymssql==2.2.11`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hittrax-dashboard.git
cd hittrax-dashboard
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure the database connection:
   - Update the settings in `config.py` with your HitTrax database credentials
   - Run the initial setup script:
```bash
python db/setup.py
```

5. Start the dashboard:
```bash
python app.py
```

The dashboard will be available at `http://127.0.0.1:8050/`

## Project Structure

```
hittrax-dashboard/
├── app.py                    # Main application entry point
├── analyze_database_structure.py  # Database analysis utility
├── assets/
│   └── styles.css           # Custom CSS styles
├── callbacks.py             # Dash callback functions
├── config.py               # Configuration settings
├── db/                     # Database-related modules
│   ├── config.py          # Database configuration
│   ├── schema.py          # Database schema definitions
│   ├── setup.py           # Database setup script
│   ├── sync.py            # Data synchronization
│   ├── sync_utils.py      # Sync helper functions
│   └── test_data.py       # Data testing utilities
├── layouts.py              # UI layout components
├── leaderboard_layout.py   # Leaderboard specific layouts
├── leaderboard_utils.py    # Leaderboard helper functions
├── requirements.txt        # Project dependencies
├── sqlite_utils.py         # SQLite database utilities
├── test_connection.py      # Database connection testing
└── utils.py               # General utility functions
```

## Features in Detail

### Data Synchronization
- Automatic synchronization between HitTrax SQL Server and local SQLite database
- Configurable sync intervals and data retention
- Unit conversion handling (metric to imperial)

### Analytics Dashboard
- Player performance metrics
- Session-by-session analysis
- Comparative analytics across skill levels
- Export capabilities for further analysis

### Leaderboards System
- Dynamic leaderboard generation
- Multiple ranking categories
- Graduation year-based grouping
- Minimum qualification thresholds

# Configuration Guide

## Database Configuration

### SQL Server Requirements
- Microsoft SQL Server 2016 or later
- SQL Server Authentication enabled
- TCP/IP protocol enabled in SQL Server Configuration Manager
- Port 1433 (default) or your custom port open in firewall

#### Required SQL Server Configuration Steps:
1. Enable SQL Server Authentication:
   - Open SQL Server Management Studio
   - Right-click your server > Properties > Security
   - Enable "SQL Server and Windows Authentication mode"
   - Restart SQL Server service

2. Enable TCP/IP:
   - Open SQL Server Configuration Manager
   - SQL Server Network Configuration > Protocols
   - Enable TCP/IP
   - Restart SQL Server service

3. Configure Firewall:
   - Open Windows Firewall with Advanced Security
   - New Inbound Rule > Port
   - TCP, Specific local ports: 1433 (or your custom port)
   - Allow the connection
   - Apply to Domain, Private, and Public as needed

### Configuration Files Setup

1. Root `config.py`:
```python
HITTRAX_CONFIG = {
    'source_db': {
        'server': 'your_server_name_or_ip',  # e.g., '192.168.1.100'
        'port': 1337,                        # Your SQL Server port
        'database': 'HitTrax',               # Your database name
        'user': r'YourUsername',             # Use r'' for Windows auth
        'password': 'your_password',
        'tds_version': '7.0',                # Important for older SQL Servers
        'charset': 'UTF-8'
    },
    'sqlite_db': 'hittrax_local.db',         # Local database path
    'conversions': {
        'meters_to_feet': 3.28084,
        'mps_to_mph': 2.23694
    }
}
```

2. `db/config.py`:
```python
DB_CONFIG = {
    'sync_interval': 86400,  # 24 hours in seconds
    'retention_days': 365,   # How long to keep historical data
    'batch_size': 1000      # Records per sync batch
}
```

### TDS Version Note
This project specifically uses TDS version 7.0 due to compatibility requirements with older SQL Server installations (circa 2016). The default TDS version in modern Python SQL libraries (8.0) may not work with older SQL Server versions. If you're encountering connection issues, verify that:

1. Your SQL Server version matches the TDS protocol version
2. The user account has appropriate permissions
3. The network connection is not blocked by firewalls

Common TDS version compatibility:
- SQL Server 2016: TDS 7.0 - 7.4
- SQL Server 2019+: TDS 7.0 - 8.0

### Troubleshooting Common Issues

1. Connection Failures:
```python
# Test your connection with:
python test_connection.py
```

2. Authentication Issues:
- Verify SQL Server Authentication is enabled
- Ensure username format matches authentication mode:
  - Windows Auth: `r'DOMAIN\Username'` or `r'COMPUTER\Username'`
  - SQL Auth: `'Username'`

3. Protocol Issues:
- Verify SQL Server Browser service is running for named instances
- Check SQL Server error logs for connection attempts
- Use SQL Server Configuration Manager to verify protocol settings

### Local Database Setup

The application uses SQLite for local caching and improved performance. This is particularly useful for:
- Reducing latency during query operations
- Enabling offline functionality
- Running scheduled tasks (e.g., midnight cron jobs on VM)

The local database is automatically created and maintained through:
```bash
python db/setup.py
```

### Cron Job Setup (Optional)

For automatic synchronization, add to crontab:
```bash
0 0 * * * cd /path/to/hittrax-dashboard && /path/to/venv/bin/python db/sync.py
```

This runs the synchronization daily at midnight.

## Performance Considerations

- The local SQLite database significantly reduces query latency
- Batch processing during sync operations minimizes memory usage
- Indexes are automatically created for commonly queried fields
- Data retention policies prevent unlimited database growth

## Configuration

The application uses two levels of configuration:
1. Root `config.py` for application settings
2. `db/config.py` for database-specific settings

Update these files with your specific configuration before running the application.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
