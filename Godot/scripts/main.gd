extends Node3D

const UNIT_DEFS := {
    "villager": {"hp": 40.0, "damage": 3.0, "speed": 4.0, "food": 50, "wood": 0, "gold": 0, "color": Color(0.25, 0.55, 0.95)},
    "militia": {"hp": 60.0, "damage": 8.0, "speed": 4.5, "food": 60, "wood": 0, "gold": 20, "color": Color(0.9, 0.25, 0.25)},
    "archer": {"hp": 45.0, "damage": 6.0, "speed": 4.7, "food": 0, "wood": 30, "gold": 40, "color": Color(0.35, 0.85, 0.35)},
    "knight": {"hp": 120.0, "damage": 14.0, "speed": 5.2, "food": 80, "wood": 0, "gold": 70, "color": Color(0.88, 0.65, 0.15)}
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
    shape.position = Vector3(0, -0.1, 0)
    ground_body.add_child(shape)
    add_child(ground_body)

    camera = Camera3D.new()
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    camera.current = true
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

func _make_town(name: String, pos: Vector3, is_player: bool) -> Node3D:
    var root := Node3D.new()
    root.name = name
    root.position = pos
    add_child(root)

    var base := _box(Vector3(12, 0.6, 12), Vector3(0, 0.3, 0), Color(0.46, 0.42, 0.34))
    root.add_child(base)

    var body_color := Color(0.64, 0.50, 0.31)
    var roof_color := Color(0.35, 0.19, 0.08)
    if not is_player:
        body_color = Color(0.55, 0.27, 0.24)
        roof_color = Color(0.32, 0.08, 0.08)

    root.add_child(_box(Vector3(9, 4.4, 7), Vector3(0, 2.6, 0.4), body_color))
    root.add_child(_box(Vector3(11, 0.35, 9), Vector3(0, 5.1, 0.4), roof_color))

    var banner_color := Color(0.10, 0.28, 0.72)
    if not is_player:
        banner_color = Color(0.72, 0.10, 0.10)
    root.add_child(_box(Vector3(1.2, 2.0, 0.12), Vector3(0, 4.3, -3.65), banner_color))
    return root

func _make_resource(name: String, pos: Vector3, size: float, color: Color) -> void:
    var node := MeshInstance3D.new()
    node.name = name
    node.position = pos
    var mesh: Mesh
    if name == "Tree":
        var cyl := CylinderMesh.new()
        cyl.top_radius = size * 0.45
        cyl.bottom_radius = size * 0.55
        cyl.height = size * 1.8
        mesh = cyl
        node.position.y = size * 0.9
    else:
        var sphere := SphereMesh.new()
        sphere.radius = size
        sphere.height = size * 2.0
        mesh = sphere
        node.position.y = size
    node.mesh = mesh
    node.material_override = _material(color)
    add_child(node)

func _spawn_unit(kind: String, pos: Vector3, is_player: bool) -> void:
    var def: Dictionary = UNIT_DEFS[kind]
    var body := CharacterBody3D.new()
    body.name = kind.capitalize()
    body.position = pos
    body.set_meta("kind", kind)
    body.set_meta("player", is_player)
    body.set_meta("hp", def["hp"])

    var mesh_node := MeshInstance3D.new()
    var sphere := SphereMesh.new()
    sphere.radius = 0.65
    sphere.height = 1.3
    mesh_node.mesh = sphere
    var unit_color: Color = def["color"]
    if not is_player:
        unit_color = Color(0.78, 0.15, 0.15)
    mesh_node.material_override = _material(unit_color)
    body.add_child(mesh_node)

    var collision := CollisionShape3D.new()
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.55
    capsule.height = 1.2
    collision.shape = capsule
    body.add_child(collision)

    add_child(body)
    units.append({"node": body, "kind": kind, "player": is_player})

func _build_ui() -> void:
    var canvas := CanvasLayer.new()
    add_child(canvas)

    var top := ColorRect.new()
    top.name = "TopBar"
    top.size = Vector2(1280, 48)
    top.color = Color(0.08, 0.06, 0.04, 0.92)
    canvas.add_child(top)

    ui_label = Label.new()
    ui_label.position = Vector2(16, 12)
    ui_label.add_theme_font_size_override("font_size", 18)
    canvas.add_child(ui_label)

    var panel := HBoxContainer.new()
    panel.name = "TrainingBar"
    panel.position = Vector2(10, 650)
    panel.size = Vector2(1260, 60)
    canvas.add_child(panel)

    for kind in ["villager", "militia", "archer", "knight"]:
        var button := Button.new()
        var def: Dictionary = UNIT_DEFS[kind]
        button.text = kind.capitalize() + " · " + _cost_text(def)
        button.custom_minimum_size = Vector2(260, 52)
        button.pressed.connect(_train.bind(kind))
        panel.add_child(button)
    _update_ui()

func _cost_text(def: Dictionary) -> String:
    var parts: Array[String] = []
    if def["wood"] > 0:
        parts.append(str(def["wood"]) + "W")
    if def["food"] > 0:
        parts.append(str(def["food"]) + "F")
    if def["gold"] > 0:
        parts.append(str(def["gold"]) + "G")
    return " ".join(parts)

func _train(kind: String) -> void:
    var def: Dictionary = UNIT_DEFS[kind]
    if population >= population_cap:
        return
    if wood < def["wood"] or food < def["food"] or gold < def["gold"]:
        return
    wood -= def["wood"]
    food -= def["food"]
    gold -= def["gold"]
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
        _update_camera()
    elif event is InputEventScreenTouch and event.pressed:
        _select_at(event.position)
    elif event is InputEventScreenDrag:
        camera_focus += Vector3(-event.relative.x * 0.03, 0, -event.relative.y * 0.03)
        _update_camera()

func _select_at(screen_pos: Vector2) -> void:
    if camera == null:
        return
    var from := camera.project_ray_origin(screen_pos)
    var direction := camera.project_ray_normal(screen_pos)
    var query := PhysicsRayQueryParameters3D.create(from, from + direction * 1000.0)
    var hit := get_world_3d().direct_space_state.intersect_ray(query)
    if hit.is_empty():
        _clear_selection()
        return
    var collider: Node = hit["collider"]
    for unit_data in units:
        var node: Node3D = unit_data["node"]
        if collider == node or collider.is_ancestor_of(node):
            if unit_data["player"]:
                _set_selection(node)
                return
    _clear_selection()

func _move_selected(screen_pos: Vector2) -> void:
    if selected_unit == null:
        return
    var from := camera.project_ray_origin(screen_pos)
    var direction := camera.project_ray_normal(screen_pos)
    var ground := Plane(Vector3.UP, 0.0)
    var hit := ground.intersects_ray(from, direction)
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
    if selected_ring != null:
        selected_ring.queue_free()
    selected_ring = null
    selected_unit = null

func _process(delta: float) -> void:
    for unit_data in units:
        var node: CharacterBody3D = unit_data["node"]
        if not is_instance_valid(node):
            continue
        if node.has_meta("destination"):
            var destination: Vector3 = node.get_meta("destination")
            var movement: Vector3 = node.global_position.direction_to(destination)
            movement.y = 0
            node.velocity = movement * UNIT_DEFS[unit_data["kind"]]["speed"]
            node.move_and_slide()
            if node.global_position.distance_to(destination) < 0.2:
                node.global_position = destination
                node.remove_meta("destination")
                node.velocity = Vector3.ZERO

func _update_camera() -> void:
    if camera == null:
        return
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
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.roughness = 0.82
    return material
