#!/usr/bin/env ruby
require  '/var/www/openshift/broker/config/environment'

# todo randomly genearte usage_type

def gen_uuid
  `uuidgen -t`.chomp.delete('-')
end

def create_domain(namespace)
  d = Domain.new
  d.namespace = namespace
  d.canonical_namespace = namespace
  d.created_at = Time.now.utc
  d.updated_at = Time.now.utc
  d.save!
  return d
end

def create_user
  u = CloudUser.new
  u.login = "user_" + gen_uuid
  u.save!
  return u
end

# Create domain pending_ops
domain_ops_types = %w[change_members add_domain_ssh_keys delete_domain_ssh_keys add_env_variables remove_env_variables]
domain_ops_types.each_with_index do |op, idx| 
  d = create_domain("domain#{idx}")
  pending_ops = PendingDomainOps.new(op_type: op, arguments: { "keys_attrs" => nil }, on_apps: nil, created_at: Time.now, state: "init") 
  Domain.where(_id: d._id).update_all({"$push" => {pending_ops: pending_ops.serializable_hash_with_timestamp}})
end


# Create user pending_ops
user_ops_types = %w[add_ssh_key delete_ssh_key]
user_ops_types.each do |op|
  u = create_user
  pending_ops = PendingUserOps.new(op_type: op, state: 'init')
  CloudUser.where(_id: u._id).update_all({"$push" => {pending_ops: pending_ops.serializable_hash_with_timestamp}}) 
end 


# Create app pending_op_groups and pending_ops
app_ops_types = %w[create_group_instance init_gear delete_gear destroy_group_instance reserve_uid unreserve_uid expose_port new_component del_component add_component post_configure_component remove_component create_gear track_usage register_dns deregister_dns register_routing_dns publish_routing_info destroy_gear start_component stop_component restart_component reload_component_config tidy_component update_configuration add_broker_auth_key remove_broker_auth_key set_group_overrides execute_connections unsubscribe_connections set_gear_additional_filesystem_gb add_alias remove_alias add_ssl_cert remove_ssl_cert patch_user_env_vars replace_all_ssh_keys]

app_pending_op_groups_types = %w[change_members update_configuration add_features remove_features make_ha update_component_limits delete_app remove_gear scale_by replace_all_ssh_keys add_alias remove_alias add_ssl_cert remove_ssl_cert patch_user_env_vars add_broker_auth_key remove_broker_auth_key start_app stop_app restart_app reload_app_config tidy_app start_feature stop_feature restart_feature reload_feature_config start_component stop_component restart_component reload_component_config execute_connections]


app_pending_op_groups_types.each_with_index do |opg, idx|
  a = Application.new
  d = create_domain("da#{idx}")
  u = create_user
  a.name = "app#{gen_uuid}".slice(0..31)
  a.created_at = Time.now.utc
  a.updated_at = Time.now.utc
  a.domain_namespace = d.namespace
  a.domain_id = d._id
  a.owner_id = u._id
  a.save!
  pending_op_groups = PendingAppOpGroup.new(op_type: opg)
  Application.where(_id: a._id).update_all({"$push" => {pending_op_groups: pending_op_groups.serializable_hash_with_timestamp}})

  app_ops_types.each_with_index do |op, i|
    pending_ops = PendingAppOp.new(op_type: op, state: 'init')
    doc = {"_id" => pending_ops._id, 
           "op_type" => op, 
           "retry_count" => 0, 
           "state" => 'init', 
           "args" =>{"gear_ref" => gen_uuid,
                     "app_name" => a.name,
                     "additional_filesystem_gb" => 0,
                     "parent_user_id" => nil,
                     "event" => "begin",
                     "user_id" => u._id,
                     "usage_type" => "GEAR_USAGE",
                     "gear_size" => "small",
                     "added" => true,
                     "removed" => true,
                     "changed" => true,
                     "push" => "TEST"
                    },
           "saved_values" => {"additional_filesystem_gb" => 0,
                              "group_overrides" => []
                             }
          }
    Application.where(_id: a._id).update_all({"$push" => { "pending_op_groups.0.pending_ops" => doc}})
  end
end
