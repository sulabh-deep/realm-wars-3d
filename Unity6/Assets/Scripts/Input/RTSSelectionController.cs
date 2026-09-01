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

        private void Start()
        {
            cam = Camera.main;
        }

        private void Update()
        {
            if (cam == null) cam = Camera.main;
            var mouse = Mouse.current;
            if (mouse == null || cam == null) return;

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
                bool tap = Vector2.Distance(pressPosition, release) < 12f && Time.unscaledTime - pressTime < 0.45f;
                if (tap) HandleTap(release);
            }

            if (mouse.rightButton.wasPressedThisFrame)
            {
                Ray ray = cam.ScreenPointToRay(mouse.position.ReadValue());
                if (Physics.Raycast(ray, out var hit, 1000f))
                {
                    foreach (var unit in selected)
                        if (unit != null) unit.SetDestination(hit.point);
                }
            }
        }

        private void HandleTap(Vector2 screenPosition)
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

        private void ClearSelection()
        {
            foreach (var unit in selected)
                if (unit != null) unit.SetSelected(false);
            selected.Clear();
        }
    }
}
