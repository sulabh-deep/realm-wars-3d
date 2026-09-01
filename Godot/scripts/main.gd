extends Node3D

const UNIT_DEFS := {
    "villager": {"hp": 40.0, "damage": 3.0, "range": 0.0, "speed": 4.0, "food": 50, "wood": 0, "gold": 0, "color": Color(0.25, 0.55, 0.95)},
    "militia": {"hp": 60.0, "damage": 8.0, "range": 0.0, "speed": 4.5, "food": 60, "wood": 0, "gold": 20, "color": Color(0.9, 0.25, 0.25)},
    "archer": {"hp": 45.0, "damage": 6.0, "range": 8.0, "speed": 4.7, "food": 0, "wood": 30, "gold": 40, "color": Color(0.35, 0.85, 0.35)},
    "knight": {"hp": 120.0, "damage": 14.0, "range": 0.0, "speed": 5.2, "food": 80, "wood": 0, "gold": 70, "color": Color(0.88, 0.65, 0.15)}
}

var wood := 250
var food := 250
var gold := 150
var population := 3
var population_cap := 50

var units: Array[Dictionary] = []
var player_town: Node3D
var enemy_town: Node3D
var selected_unit: Node3D
var selected_ring: MeshInstance3D
var camera: Camera3D
var yaw := 45.0
var camera_distance := 30.0
var camera_focus := Vector3.ZERO
var dragging := false
var last_mouse := Vector2.ZERO
var ui_label: Label

func _ready() -> void:
    Engine.max_fps = 60
    _build_world()
    _build_ui()

func _build_world() -> void:
    var env := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("78c8e5")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.75, 0.82, 0.72)
    environment.ambient_light_energy = 0.75
    env.environment = environment
    add_child(env)

    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-50, -30, 0)
    sun.light_energy = 1.15
    sun.shadow_enabled = true
    add_child(sun)

    var ground := MeshInstance3D.new()
    var plane := PlaneMesh.new()
    plane.size = Vector2(220, 220)
    ground.mesh = plane
    ground.material_override = _material(Color(0.47, 0.64, 0.35))
    add_child(ground)
    var ground_body := StaticBody3D.new()
    var shape := CollisionShape3D.new()
    var box := BoxShape3D.new()
    box.size = Vector3(220, 0.2, 220)
    shape.shape = box
    shape.position.y = -0.1
    ground_body.add_child(shape)
    add_child(ground_body)

    camera = Camera3D.new()
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    add_child(camera)
    _update_camera()

    player_town = _make_town("Player Town Center", Vector3.ZERO, true)
    enemy_town = _make_town("Enemy Town Center", Vector3(32, 0, -24), false)

    for i in 12:
        var p := Vector3(randf_range(-50, 50), 0, randf_range(-40, 40))
        _make_resource("Tree", p, 2.5, Color(0.12, 0.40, 0.08))
    for i in 4:
        var p := Vector3(randf_range(-45, 45), 0, randf_range(-35, 35))
        _make_resource("Gold Vein", p, 1.1, Color(0.90, 0.63, 0.10))

    for i in 3:
        _spawn_unit("villager", Vector3(-3 + i * 2, 0.75, 4), true)

func _make_town(name: String, pos: Vector3, player: bool) -> Node3D:
    var root := Node3D.new()
    root.name = name
    root.position = pos
    add_child(root)
    var base := _box(Vector3(12, 0.6, 12), Vector3(0, 0.3, 0), Color(0.46, 0.42, 0.34))
    root.add_child(base)
    root.add_child(_box(Vector3(9, 4.4, 7), Vector3(0, 2.6, 0.4), player ? Color(0.64, 0.50, 0.31) : Color(0.55, 0.27, 0.24)))
    root.add_child(_box(Vector3(11, 0.35, 9), Vector3(0, 5.1, 0.4), player ? Color(0.35, 0.19, 0.08) : Color(0.32, 0.08, 0.08)))
    root.add_child(_box(Vector3(1.2, 2.0, 0.12), Vector3(0, 4.3, -3.65), player ? Color(0.10, 0.28, 0.72) : Color(0.72, 0.10, 0.10)))
    var tower := MeshInstance3D.new()
    var cyl := CylinderMesh.new()
    cyl.top_radius = 0.7
    cyl.bottom_radius = 0.7
    cyl.height = 3.2
    tower.mesh = cyl
    tower.position = Vector3(0, 6.7, 0)
    tower.material_override = _material(player ? Color(0.55, 0.38, 0.20) : Color(0.45, 0.20, 0.18))
    root.add_child(tower)
    return root

func _make_resource(name: String, pos: Vector3, scale: float, color: Color) -> void:
    var node := MeshInstance3D.new()
    node.name = name
    node.position = pos + Vector3.UP * (name == "Tree" ? scale * 0.7 : scale)
    var mesh: Mesh
    if name == "Tree":
        var cyl := CylinderMesh.new()
        cyl.top_radius = scale * 0.45
        cyl.bottom_radius = scale * 0.55
        cyl.height = scale * 1.8
        mesh = cyl
    else:
        var sphere := SphereMesh.new()
        sphere.radius = scale
        sphere.height = scale * 2.0
        mesh = sphere
    node.mesh = mesh
    node.material_override = _material(color)
    add_child(node)

func _spawn_unit(kind: String, pos: Vector3, player: bool) -> void:
    var def: Dictionary = UNIT_DEFS[kind]
    var body := CharacterBody3D.new()
    body.name = def["name"] if def.has("name") else kind.capitalize()
    body.position = pos
    var mesh_node := MeshInstance3D.new()
    var sphere := SphereMesh.new()
    sphere.radius = 0.65
    sphere.height = 1.3
    mesh_node.mesh = sphere
    mesh_node.material_override = _material(def["color"] if player else Color(0.78, 0.15, 0.15))
    body.add_child(mesh_node)
    var collision := CollisionShape3D.new()
    var shape := CapsuleShape3D.new()
    shape.radius = 0.55
    shape.height = 1.2
    collision.shape = shape
    body.add_child(collision)
    add_child(body)
    units.append({"node": body, "kind": kind, "player": player, "hp": def["hp"], "destination": body.position, "moving": false})

func _build_ui() -> void:
    var canvas := CanvasLayer.new()
    add_child(canvas)
    var top := ColorRect.new()
    top.position = Vector2(0, 0)
    top.size = Vector2(1280, 48)
    top.color = Color(0.08, 0.06, 0.04, 0.92)
    canvas.add_child(top)
    ui_label = Label.new()
    ui_label.position = Vector2(16, 12)
    ui_label.add_theme_font_size_override("font_size", 18)
    canvas.add_child(ui_label)
    var panel := HBoxContainer.new()
    panel.position = Vector2(10, 650)
    panel.size = Vector2(1260, 60)
    canvas.add_child(panel)
    for kind in ["villager", "militia", "archer", "knight"]:
        var b := Button.new()
        var d: Dictionary = UNIT_DEFS[kind]
        b.text = kind.capitalize() + " · " + _cost_text(d)
        b.custom_minimum_size = Vector2(260, 52)
        b.pressed.connect(func(): _train(kind))
        panel.add_child(b)
    _update_ui()

func _cost_text(d: Dictionary) -> String:
    var parts: Array[String] = []
    if d["wood"] > 0: parts.append(str(d["wood"]) + "W")
    if d["food"] > 0: parts.append(str(d["food"]) + "F")
    if d["gold"] > 0: parts.append(str(d["gold"]) + "G")
    return " ".join(parts)

func _train(kind: String) -> void:
    var d: Dictionary = UNIT_DEFS[kind]
    if population >= population_cap: return
    if wood < d["wood"] or food < d["food"] or gold < d["gold"]: return
    wood -= d["wood"]
    food -= d["food"]
    gold -= d["gold"]
    population += 1
    _spawn_unit(kind, player_town.position + Vector3(6, 0.75, 5), true)
    _update_ui()

func _update_ui() -> void:
    if ui_label:
        ui_label.text = "WOOD %d    FOOD %d    GOLD %d    POP %d/%d" % [wood, food, gold, population, population_cap]

func _input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_MIDDLE:
            dragging = event.pressed
            last_mouse = event.position
        elif event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
            _select_at(event.position)
        elif event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
            _move_selected(event.position)
        elif event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
            camera_distance = max(16.0, camera_distance - 2.0)
            _update_camera()
        elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
            camera_distance = min(48.0, camera_distance + 2.0)
            _update_camera()
    elif event is InputEventMouseMotion and dragging:
        yaw -= event.relative.x * 0.18
        last_mouse = event.position
        _update_camera()
    elif event is InputEventScreenTouch and event.pressed:
        _select_at(event.position)
    elif event is InputEventScreenDrag:
        pass

func _select_at(screen_pos: Vector2) -> void:
    if not camera: return
    var from := camera.project_ray_origin(screen_pos)
    var dir := camera.project_ray_normal(screen_pos)
    var query := PhysicsRayQueryParameters3D.create(from, from + dir * 1000.0)
    var hit := get_world_3d().direct_space_state.intersect_ray(query)
    if hit.is_empty():
        _clear_selection()
        return
    var collider: Node = hit["collider"]
    for u in units:
        if u["node"] == collider or collider.is_ancestor_of(u["node"]):
            if u["player"]:
                _set_selection(u["node"])
                return
    _clear_selection()

func _move_selected(screen_pos: Vector2) -> void:
    if selected_unit == null: return
    var from := camera.project_ray_origin(screen_pos)
    var dir := camera.project_ray_normal(screen_pos)
    var plane := Plane(Vector3.UP, 0.0)
    var hit := plane.intersects_ray(from, dir)
    if hit != null:
        selected_unit.set_meta("destination", hit)

func _set_selection(node: Node3D) -> void:
    _clear_selection()
    selected_unit = node
    selected_ring = MeshInstance3D.new()
    var ring := CylinderMesh.new()
    ring.top_radius = 0.9
    ring.bottom_radius = 0.9
    ring.height = 0.04
    selected_ring.mesh = ring
    selected_ring.material_override = _material(Color(1.0, 0.92, 0.18))
    selected_ring.position = Vector3(0, -0.62, 0)
    selected_unit.add_child(selected_ring)

func _clear_selection() -> void:
    if selected_ring:
        selected_ring.queue_free()
    selected_ring = null
    selected_unit = null

func _process(delta: float) -> void:
    for u in units:
        var node: CharacterBody3D = u["node"]
        if not is_instance_valid(node): continue
        if node.has_meta("destination"):
            var dest: Vector3 = node.get_meta("destination")
            node.velocity = node.position.direction_to(dest) * UNIT_DEFS[u["kind"]]["speed"]
            node.velocity.y = 0
            node.move_and_slide()
            if node.position.distance_to(dest) < 0.15:
                node.position = dest
                node.remove_meta("destination")
                node.velocity = Vector3.ZERO
    if get_viewport().size.x != 1280:
        _layout_ui()

func _layout_ui() -> void:
    for child in get_children():
        if child is CanvasLayer:
            var boxes := child.get_children()
            if boxes.size() >= 2:
                boxes[0].size.x = get_viewport().size.x
                boxes[1].position = Vector2(16, 12)
                if boxes.size() >= 2 and boxes[2] is HBoxContainer:
                    boxes[2].position = Vector2(10, get_viewport().size.y - 68)
                    boxes[2].size.x = get_viewport().size.x - 20

func _update_camera() -> void:
    if not camera: return
    var r := deg_to_rad(yaw)
    camera.position = camera_focus + Vector3(sin(r) * camera_distance, camera_distance * 0.72, cos(r) * camera_distance)
    camera.look_at(camera_focus, Vector3.UP)
    camera.size = lerp(8.0, 30.0, inverse_lerp(16.0, 48.0, camera_distance))

func _box(size: Vector3, pos: Vector3, color: Color) -> MeshInstance3D:
    var node := MeshInstance3D.new()
    var box := BoxMesh.new()
    box.size = size
    node.mesh = box
    node.position = pos
    node.material_override = _material(color)
    return node

func _material(color: Color) -> StandardMaterial3D:
    var m := StandardMaterial3D.new()
    m.albedo_color = color
    m.roughness = 0.82
    return m
