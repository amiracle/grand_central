#############
# CONSTANTS #
#############

WORKLOAD_ID = '8ae0f2a5baf254fc90aae33135eae088'
LENS_ALIAS = 'wellarchitected'
PILLAR_IDS = [
    'security', 
    'reliability', 
    'operationalExcellence', 
    'performance', 
    'costOptimization'
]

#####################
# ANSWERS BY PILLAR #
#####################

# Security
ANS_CREDENTIAL_MANAGEMENT = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'credential-management',
    'SelectedChoices': [
        'sec_credential_management_define',
        'sec_credential_management_root',
        'sec_credential_management_mfa',
        'sec_credential_management_enforcement',
        'sec_credential_management_centralized',
        'sec_credential_management_password',
        'sec_credential_management_rotate',
        'sec_credential_management_audit'
    ],
    'IsApplicable': True,
}
ANS_IDENTITY_HUMAN = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'identity-human',
    'SelectedChoices': [
        'sec_identity_human_define',
        'sec_identity_human_least',
        'sec_identity_human_unique',
        'sec_identity_human_lifecycle',
        'sec_identity_human_auto_mgmt',
        'sec_identity_human_roles'
    ],
    'IsApplicable': True,
}
ANS_IDENTITY_PROGRAMMATIC = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'identity-programmatic',
    'SelectedChoices': [
        'sec_identity_programmatic_define',
        'sec_identity_programmatic_least',
        'sec_identity_programmatic_auto_mgmt',
        'sec_identity_programmatic_roles',
        'sec_identity_programmatic_dynamic'
    ],
    'IsApplicable': True,
}
ANS_INVESTIGATE_EVENTS = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'detect-investigate-events',
    'SelectedChoices': [
        'sec_detect_investigate_events_define_logs',
        'sec_detect_investigate_events_define_alerts',
        'sec_detect_investigate_events_define_metrics',
        'sec_detect_investigate_events_app_service_logging',
        'sec_detect_investigate_events_analyze',
        'sec_detect_investigate_events_auto_alert',
        'sec_detect_investigate_events_develop_processes'
    ],
    'IsApplicable': True,
}
ANS_SECURITY_AWARENESS = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'security-awareness',
    'SelectedChoices': [
        'sec_security_awareness_bus_requirements',
        'sec_security_awareness_practices',
        'sec_security_awareness_threats',
        'sec_security_awareness_evaluate_new',
        'sec_security_awareness_threat_model',
        'sec_security_awareness_implement'
    ],
    'IsApplicable': True,
}
ANS_NETWORK_PROTECTION = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'network-protection',
    'SelectedChoices': [
        'sec_network_protection_define_requirements',
        'sec_network_protection_limit_exposure',
        'sec_network_protection_auto_config',
        'sec_network_protection_auto_protect',
        'sec_network_protection_inspection',
        'sec_network_protection_layered'
    ],
    'IsApplicable': True,
}
ANS_PROTECT_COMPUTE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'protect-compute',
    'SelectedChoices': [
        'sec_protect_compute_define_requirements',
        'sec_protect_compute_scan_patch',
        'sec_protect_compute_auto_config',
        'sec_protect_compute_auto_protection',
    ],
    'IsApplicable': True,
}
ANS_DATA_CLASSIFICATION = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'data-classification',
    'SelectedChoices': [
        'sec_data_classification_define_requirements',
        'sec_data_classification_define_protection',
        'sec_data_classification_implement_identification',
        'sec_data_classification_auto_classification',
        'sec_data_classification_identify_types'
    ],
    'IsApplicable': True,
}
ANS_PROTECT_DATA_REST = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'protect-data-rest',
    'SelectedChoices': [
        'sec_protect_data_rest_define_requirements',
        'sec_protect_data_rest_key_mgmt',
        'sec_protect_data_rest_encrypt',
        'sec_protect_data_rest_access_control',
        'sec_protect_data_rest_people_away'
    ],
    'IsApplicable': True,
}
ANS_PROTECT_DATA_TRANSIT = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'protect-data-transit',
    'SelectedChoices': [
        'sec_protect_data_transit_define_requirements',
        'sec_protect_data_transit_key_cert_mgmt',
        'sec_protect_data_transit_encrypt',
        'sec_protect_data_transit_auto_data_leak',
        'sec_protect_data_transit_authentication'
    ],
    'IsApplicable': True,
}

# Reliability
ANS_MANAGE_SERVICE_LIMITS = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'manage-service-limits',
    'SelectedChoices': [
        'rel_manage_service_limits_aware_but_no_tracking',
    ],
    'IsApplicable': True,
}
ANS_PLANNING_NETWORK_TOPOLOGY = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'planning-network-topology',
    'SelectedChoices': [
        'rel_planning_network_topology_ha_conn_private_networks',
        'rel_planning_network_topology_ha_conn_users'
    ],
    'IsApplicable': True,
}
ANS_ADAPT_TO_CHANGES = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'adapt-to-changes',
    'SelectedChoices': [
        'rel_adapt_to_changes_autoscale_adapt',
        'rel_adapt_to_changes_load_tested_adapt'
    ],
    'IsApplicable': True,
}
ANS_MONITOR_AWS_RESOURCES = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'monitor-aws-resources',
    'SelectedChoices': [
        'rel_monitor_aws_resources_monitor_resources',
        'rel_monitor_aws_resources_notification_monitor'
    ],
    'IsApplicable': True,
}
ANS_TRACKING_CHANGE_MANAGEMENT = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'tracking-change-management',
    'SelectedChoices': [
        'rel_tracking_change_management_no',
    ],
    'IsApplicable': True,
}
ANS_BACKING_UP_DATA = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'backing-up-data',
    'SelectedChoices': [
        'rel_backing_up_data_identified_backups_data',
        'rel_backing_up_data_automated_backups_data',
        'rel_backing_up_data_periodic_recovery_testing_data',
        'rel_backing_up_data_secured_backups_data'
    ],
    'IsApplicable': True,
}
ANS_WITHSTAND_COMPONENT_FAILURES = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'withstand-component-failures',
    'SelectedChoices': [
        'rel_withstand_component_failures_monitoring_health',
        'rel_withstand_component_failures_loosely_coupled_system',
        'rel_withstand_component_failures_graceful_degradation',
    ],
    'IsApplicable': True,
}
ANS_TESTING_RESILIENCY = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'testing-resiliency',
    'SelectedChoices': [
        'rel_testing_resiliency_playbook_resiliency',
        'rel_testing_resiliency_rca_resiliency',
        'rel_testing_resiliency_failure_injection_resiliency',
    ],
    'IsApplicable': True,
}
ANS_PLANNING_FOR_RECOVERY = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'planning-for-recovery',
    'SelectedChoices': [
        'rel_planning_for_recovery_objective_defined_recovery',
        'rel_planning_for_recovery_disaster_recovery',
        'rel_planning_for_recovery_dr_tested',
    ],
    'IsApplicable': True,
}

# Operational Excellence
ANS_PRIORITIES = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'priorities',
    'SelectedChoices': [
        'ops_priorities_ext_cust_needs',
        'ops_priorities_int_cust_needs'
    ],
    'IsApplicable': True,
}
ANS_TELEMETRY = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'telemetry',
    'SelectedChoices': [
        'ops_telemetry_no'
    ],
    'IsApplicable': True,
}
ANS_DEV_INTEG = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'dev-integ',
    'SelectedChoices': [
        'ops_dev_integ_version_control',
        'ops_dev_integ_test_val_chg',
        'ops_dev_integ_conf_mgmt_sys',
        'ops_dev_integ_build_mgmt_sys',
        'ops_dev_integ_code_quality'
    ],
    'IsApplicable': True,
}
ANS_MIT_DEPLOY_RISKS = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'mit-deploy-risks',
    'SelectedChoices': [
        'ops_mit_deploy_risks_plan_for_unsucessful_changes',
        'ops_mit_deploy_risks_test_val_chg',
        'ops_mit_deploy_risks_freq_sm_rev_chg'
    ],
    'IsApplicable': True,
}
ANS_READY_TO_SUPPORT = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'ready-to-support',
    'SelectedChoices': [
        'ops_ready_to_support_personnel_capability',
        'ops_ready_to_support_const_orr'
    ],
    'IsApplicable': True,
}
ANS_WORKLOAD_HEALTH = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'workload-health',
    'SelectedChoices': [
        'ops_workload_health_define_workload_kpis',
        'ops_workload_health_design_workload_metrics',
        'ops_workload_health_collect_analyze_workload_metrics'
    ],
    'IsApplicable': True,
}
ANS_OPERATIONS_HEALTH = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'operations-health',
    'SelectedChoices': [
        'ops_operations_health_define_ops_kpis',
        'ops_operations_health_design_ops_metrics',
        'ops_operations_health_collect_analyze_ops_metrics',
        'ops_operations_health_ops_outcome_alerts'
    ],
    'IsApplicable': True,
}
ANS_EVENT_RESPONSE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'event-response',
    'SelectedChoices': [
        'ops_event_response_define_escalation_paths',
        'ops_event_response_push_notify',
    ],
    'IsApplicable': True,
}
ANS_EVOLVE_OPS = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'evolve-ops',
    'SelectedChoices': [
        'ops_evolve_ops_process_cont_imp',
        'ops_evolve_ops_feedback_loops',
        'ops_evolve_ops_drivers_for_imp'
    ],
    'IsApplicable': True,
}

# Performance Efficiency
ANS_PERFORMING_ARCHITECTURE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'performing-architecture',
    'SelectedChoices': [
        'perf_performing_architecture_evaluate_resources',
        'perf_performing_architecture_process',
        'perf_performing_architecture_cost',
        'perf_performing_architecture_use_policies',
        'perf_performing_architecture_external_guidance'
    ],
    'IsApplicable': True,
}
ANS_SELECT_COMPUTE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'select-compute',
    'SelectedChoices': [
        'perf_select_compute_evaluate_options',
        'perf_select_compute_config_options',
        'perf_select_compute_collect_metrics'
    ],
    'IsApplicable': True,
}
ANS_RIGHT_STORAGE_SOLUTION = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'right-storage-solution',
    'SelectedChoices': [
        'perf_right_storage_solution_understand_char',
        'perf_right_storage_solution_evaluated_options',
        'perf_right_storage_solution_optimize_patterns'
    ],
    'IsApplicable': True,
}
ANS_RIGHT_DATABASE_SOLUTION = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'right-database-solution',
    'SelectedChoices': [
        'perf_right_database_solution_understand_char',
        'perf_right_database_solution_evaluate_options',
        'perf_right_database_solution_optimize_metrics'
    ],
    'IsApplicable': True,
}
ANS_SELECT_NETWORK = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'select-network',
    'SelectedChoices': [
        'perf_select_network_evaluate_features'
    ],
    'IsApplicable': True,
}
ANS_CONTINUE_HAVING_APPROPRIATE_RESOURCE_TYPE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'continue-having-appropriate-resource-type',
    'SelectedChoices': [
        'perf_continue_having_appropriate_resource_type_no'
    ],
    'IsApplicable': True,
}
ANS_MONITOR_INSTANCES_POST_LAUNCH = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'monitor-instances-post-launch',
    'SelectedChoices': [
        'perf_monitor_instances_post_launch_record_metrics',
        'perf_monitor_instances_post_launch_review_metrics',
        'perf_monitor_instances_post_launch_generate_alarms',
        'perf_monitor_instances_post_launch_review_metrics_collected',
        'perf_monitor_instances_post_launch_proactive'
    ],
    'IsApplicable': True,
}
ANS_TRADEOFFS_PERFORMANCE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'tradeoffs-performance',
    'SelectedChoices': [
        'perf_tradeoffs_performance_critical_areas',
        'perf_tradeoffs_performance_measure',
    ],
    'IsApplicable': True,
}

# Cost Optimization
ANS_GOVERN_USAGE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'govern-usage',
    'SelectedChoices': [
        'cost_govern_usage_policies',
        'cost_govern_usage_account_structure',
        'cost_govern_usage_groups_roles',
        'cost_govern_usage_controls',
        'cost_govern_usage_track_lifecycle'
    ],
    'IsApplicable': True,
}
ANS_MONITOR_USAGE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'monitor-usage',
    'SelectedChoices': [
        'cost_monitor_usage_enable_cur',
        'cost_monitor_usage_define_attribution',
        'cost_monitor_usage_define_kpi',
        'cost_monitor_usage_implement_tagging',
        'cost_monitor_usage_config_tools',
        'cost_monitor_usage_report',
        'cost_monitor_usage_proactive_process',
        'cost_monitor_usage_allocate_outcome'
    ],
    'IsApplicable': True,
}
ANS_DECOMISSIONING_RESOURCES = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'decomissioning-resources',
    'SelectedChoices': [
        'cost_decomissioning_resources_track',
        'cost_decomissioning_resources_define_policy',
        'cost_decomissioning_resources_ad_hoc',
        'cost_decomissioning_resources_automated'
    ],
    'IsApplicable': True,
}
ANS_SELECT_SERVICE = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'select-service',
    'SelectedChoices': [
        'cost_select_service_requirements',
        'cost_select_service_analyze_all',
        'cost_select_service_thorough_analysis',
        'cost_select_service_select_for_cost',
        'cost_select_service_analyze_over_time'
    ],
    'IsApplicable': True,
}
ANS_TYPE_SIZE_RESOURCES = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'type-size-resources',
    'SelectedChoices': [
        'cost_type_size_resources_cost_modeling',
        'cost_type_size_resources_estimate',
        'cost_type_size_resources_metrics_driven'
    ],
    'IsApplicable': True,
}
ANS_PRICING_MODEL = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'pricing-model',
    'SelectedChoices': [
        'cost_pricing_model_analysis',
        'cost_pricing_model_low_use',
        'cost_pricing_model_region_cost'
    ],
    'IsApplicable': True,
}
ANS_DATA_TRANSFER = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'data-transfer',
    'SelectedChoices': [
        'cost_data_transfer_modeling',
        'cost_data_transfer_optimized_components',
        'cost_data_transfer_implement_services'
    ],
    'IsApplicable': True,
}
ANS_CAPACITY_MATCHES_NEED = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'capacity-matches-need',
    'SelectedChoices': [
        'cost_capacity_matches_need_cost_analysis',
        'cost_capacity_matches_need_ad_hoc',
        'cost_capacity_matches_need_dynamic'
    ],
    'IsApplicable': True,
}
ANS_EVALUATE_NEW_SERVICES = {
    'WorkloadId':WORKLOAD_ID,
    'LensAlias':'wellarchitected',
    'QuestionId':'evaluate-new-services',
    'SelectedChoices': [
        'cost_evaluate_new_services_function',
        'cost_evaluate_new_services_review_process',
        'cost_evaluate_new_services_ad_hoc',
        'cost_evaluate_new_services_review_workload'
    ],
    'IsApplicable': True,
}

# Create Answer List
ANSWERS = [
    ANS_CREDENTIAL_MANAGEMENT,
    ANS_IDENTITY_HUMAN,
    ANS_IDENTITY_PROGRAMMATIC,
    ANS_INVESTIGATE_EVENTS,
    ANS_SECURITY_AWARENESS,
    ANS_NETWORK_PROTECTION,
    ANS_PROTECT_COMPUTE,
    ANS_DATA_CLASSIFICATION,
    ANS_PROTECT_DATA_REST,
    ANS_PROTECT_DATA_TRANSIT,
    ANS_MANAGE_SERVICE_LIMITS,
    ANS_PLANNING_NETWORK_TOPOLOGY,
    ANS_ADAPT_TO_CHANGES,
    ANS_MONITOR_AWS_RESOURCES,
    ANS_TRACKING_CHANGE_MANAGEMENT,
    ANS_BACKING_UP_DATA,
    ANS_WITHSTAND_COMPONENT_FAILURES,
    ANS_TESTING_RESILIENCY,
    ANS_PLANNING_FOR_RECOVERY,
    ANS_PRIORITIES,
    ANS_TELEMETRY,
    ANS_DEV_INTEG,
    ANS_MIT_DEPLOY_RISKS,
    ANS_READY_TO_SUPPORT,
    ANS_WORKLOAD_HEALTH,
    ANS_OPERATIONS_HEALTH,
    ANS_EVENT_RESPONSE,
    ANS_EVOLVE_OPS,
    ANS_PERFORMING_ARCHITECTURE,
    ANS_SELECT_COMPUTE,
    ANS_RIGHT_STORAGE_SOLUTION,
    ANS_RIGHT_DATABASE_SOLUTION,
    ANS_SELECT_NETWORK,
    ANS_CONTINUE_HAVING_APPROPRIATE_RESOURCE_TYPE,
    ANS_MONITOR_INSTANCES_POST_LAUNCH,
    ANS_TRADEOFFS_PERFORMANCE,
    ANS_GOVERN_USAGE,
    ANS_MONITOR_USAGE,
    ANS_DECOMISSIONING_RESOURCES,
    ANS_SELECT_SERVICE,
    ANS_TYPE_SIZE_RESOURCES,
    ANS_PRICING_MODEL,
    ANS_DATA_TRANSFER,
    ANS_CAPACITY_MATCHES_NEED,
    ANS_EVALUATE_NEW_SERVICES
]