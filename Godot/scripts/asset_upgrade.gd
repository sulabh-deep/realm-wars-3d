extends Node

func _ready() -> void:
    call_deferred("_replace_world_assets")

func _replace_world_assets() -> void:
    _replace_town("Player Town Center")
    _replace_town("Enemy Town Center")
    var root: Node = get_parent()
    for child in root.get_children():
        if child is Node3D and (child.name.begins_with("Tree") or child.name.begins_with("Gold Vein")):
            _replace_resource(child)

func _load_model(path: String) -> PackedScene:
    if not ResourceLoader.exists(path):
        return null
    return load(path) as PackedScene

func _replace_town(node_name: String) -> void:
    var town := get_parent().get_node_or_null(NodePath(node_name))
    if town == null:
        return
    var packed: PackedScene = _load_model("res://assets/town-center/stage1.glb")
    if packed == null:
        return
    for child in town.get_children():
        child.queue_free()
    var model := packed.instantiate()
    model.name = "Stage1"
    town.add_child(model)

func _replace_resource(node: Node3D) -> void:
    var path: String = "res://assets/resources/tree.glb" if node.name.begins_with("Tree") else "res://assets/resources/gold-vein.glb"
    var packed: PackedScene = _load_model(path)
    if packed == null:
        return
    for child in node.get_children():
        child.queue_free()
    var model := packed.instantiate()
    node.add_child(model)
