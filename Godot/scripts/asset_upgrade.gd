extends Node

func _ready() -> void:
    call_deferred("_replace_world_assets")

func _replace_world_assets() -> void:
    _replace_town("Player Town Center")
    _replace_town("Enemy Town Center")
    var root := get_parent()
    for child in root.get_children():
        if child is Node3D and (child.name.begins_with("Tree") or child.name.begins_with("Gold Vein")):
            _replace_resource(child)

func _replace_town(node_name: String) -> void:
    var town := get_parent().get_node_or_null(NodePath(node_name))
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

func _replace_resource(node: Node3D) -> void:
    var path := "res://assets/resources/tree.glb" if node.name.begins_with("Tree") else "res://assets/resources/gold-vein.glb"
    var packed := load(path) as PackedScene
    if packed == null:
        return
    for child in node.get_children():
        child.queue_free()
    var model := packed.instantiate()
    node.add_child(model)
