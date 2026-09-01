extends Node

func _ready() -> void:
    call_deferred("_replace_world_assets")

func _replace_world_assets() -> void:
    _replace_town("Player Town Center", true)
    _replace_town("Enemy Town Center", false)
    for node in get_tree().get_nodes_in_group("procedural_resources"):
        if is_instance_valid(node):
            _replace_resource(node)

func _replace_town(node_name: String, player: bool) -> void:
    var root := get_parent().get_node_or_null("Node3D")
    if root == null:
        root = get_parent()
    var town := root.get_node_or_null(node_name)
    if town == null:
        return
    var packed := load("res://assets/town-center/stage1.glb") as PackedScene
    if packed == null:
        return
    for child in town.get_children():
        child.queue_free()
    var model := packed.instantiate()
    model.name = "Stage1"
    town.add_child(model)
    town.scale = Vector3.ONE

func _replace_resource(node: Node3D) -> void:
    var path := "res://assets/resources/tree.glb" if node.name.begins_with("Tree") else "res://assets/resources/gold-vein.glb"
    var packed := load(path) as PackedScene
    if packed == null:
        return
    for child in node.get_children():
        child.queue_free()
    var model := packed.instantiate()
    node.add_child(model)
