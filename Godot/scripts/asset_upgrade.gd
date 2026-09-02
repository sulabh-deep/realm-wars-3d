extends Node

const MODEL_ROOT := "res://runtime_assets/"
var _cache: Dictionary = {}

func _ready() -> void:
    call_deferred("_replace_world_assets")

func _replace_world_assets() -> void:
    _replace_town("Player Town Center")
    _replace_town("Enemy Town Center")
    var root: Node = get_parent()
    for child in root.get_children():
        if child is Node3D and (child.name.begins_with("Tree") or child.name.begins_with("Gold Vein")):
            _replace_resource(child)

func _load_runtime_model(path: String) -> Node:
    if _cache.has(path):
        return _cache[path]
    if not FileAccess.file_exists(path):
        return null
    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var error: Error = document.append_from_file(path, state)
    if error != OK:
        push_error("Couldn't load runtime glTF: %s (%s)" % [path, error_string(error)])
        return null
    var model: Node = document.generate_scene(state)
    if model == null:
        return null
    _cache[path] = model
    return model

func _duplicate_runtime_model(path: String) -> Node:
    var prototype: Node = _load_runtime_model(path)
    if prototype == null:
        return null
    return prototype.duplicate(Node.DUPLICATE_USE_INSTANTIATION | Node.DUPLICATE_SCRIPTS)

func _replace_town(node_name: String) -> void:
    var town := get_parent().get_node_or_null(NodePath(node_name))
    if town == null:
        return
    var model: Node = _duplicate_runtime_model(MODEL_ROOT + "town-center/stage1.glb.bin")
    if model == null:
        return
    for child in town.get_children():
        town.remove_child(child)
        child.queue_free()
    model.name = "Stage1"
    town.add_child(model)

func _replace_resource(node: Node3D) -> void:
    var filename := "tree.glb.bin" if node.name.begins_with("Tree") else "gold-vein.glb.bin"
    var model: Node = _duplicate_runtime_model(MODEL_ROOT + "resources/" + filename)
    if model == null:
        return
    for child in node.get_children():
        node.remove_child(child)
        child.queue_free()
    node.add_child(model)
