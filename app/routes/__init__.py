def register_blueprints(app):
    from .auth import bp as auth_bp
    from .dashboard import bp as dashboard_bp
    from .exhibition import bp as exhibition_bp
    from .concept import bp as concept_bp
    from .proposal import bp as proposal_bp
    from .drafts import bp as drafts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(exhibition_bp)
    app.register_blueprint(concept_bp)
    app.register_blueprint(proposal_bp)
    app.register_blueprint(drafts_bp)
