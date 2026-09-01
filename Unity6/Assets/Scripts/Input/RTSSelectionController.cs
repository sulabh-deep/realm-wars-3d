using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

namespace RealmWars3D
{
    public sealed class RTSSelectionController : MonoBehaviour
    {
        private Camera cam;
        private readonly List<Unit> selected = new();
        private Vector2 pressPosition;
        private bool pressed;
        private float pressTime;
        private bool touchPressed;
        private Vector2 touchStart;
        private float touchTime;

        private void Start() => cam = Camera.main;

        private void Update()
        {
            if (cam == null) cam = Camera.main;
            if (cam == null) return;
            HandleMouse();
            HandleTouch();
        }

        private void HandleMouse()
        {
            var mouse = Mouse.current;
            if (mouse == null) return;
            if (mouse.leftButton.wasPressedThisFrame)
            {
                pressed = true;
                pressPosition = mouse.position.ReadValue();
                pressTime = Time.unscaledTime;
            }
            if (mouse.leftButton.wasReleasedThisFrame && pressed)
            {
                pressed = false;
                var release = mouse.position.ReadValue();
                if (Vector2.Distance(pressPosition, release) < 12f && Time.unscaledTime - pressTime < 0.45f)
                    SelectAt(release);
            }
            if (mouse.rightButton.wasPressedThisFrame)
                MoveSelectedTo(mouse.position.ReadValue());
        }

        private void HandleTouch()
        {
            var touch = Touchscreen.current;
            if (touch == null || touch.touches.Count == 0) return;
            var primary = touch.touches[0];
            if (primary.press.wasPressedThisFrame)
            {
                touchPressed = true;
                touchStart = primary.position.ReadValue();
                touchTime = Time.unscaledTime;
            }
            if (primary.press.wasReleasedThisFrame && touchPressed)
            {
                touchPressed = false;
                var release = primary.position.ReadValue();
                if (Vector2.Distance(touchStart, release) < 24f && Time.unscaledTime - touchTime < 0.5f && touch.touches.Count < 2)
                    SelectAt(release);
            }
        }

        private void SelectAt(Vector2 screenPosition)
        {
            Ray ray = cam.ScreenPointToRay(screenPosition);
            if (!Physics.Raycast(ray, out var hit, 1000f))
            {
                ClearSelection();
                return;
            }
            var unit = hit.collider.GetComponentInParent<Unit>();
            if (unit == null || unit.Owner != 0)
            {
                ClearSelection();
                return;
            }
            ClearSelection();
            selected.Add(unit);
            unit.SetSelected(true);
        }

        private void MoveSelectedTo(Vector2 screenPosition)
        {
            if (selected.Count == 0) return;
            Ray ray = cam.ScreenPointToRay(screenPosition);
            if (!Physics.Raycast(ray, out var hit, 1000f)) return;
            foreach (var unit in selected)
                if (unit != null) unit.SetDestination(hit.point);
        }

        private void ClearSelection()
        {
            foreach (var unit in selected)
                if (unit != null) unit.SetSelected(false);
            selected.Clear();
        }
    }
}
