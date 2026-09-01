using UnityEngine;
using UnityEngine.InputSystem;

namespace RealmWars3D
{
    public sealed class RTSCameraController : MonoBehaviour
    {
        private Camera cam;
        private float yaw = 45f;
        private float distance = 30f;
        private Vector3 focus = Vector3.zero;
        private Vector2 lastPointer;
        private bool dragging;

        public void Initialize(Camera targetCamera) => cam = targetCamera;

        private void Update()
        {
            if (cam == null) return;

            HandlePointer();
            HandleZoom();
            UpdateTransform();
        }

        private void HandlePointer()
        {
            var mouse = Mouse.current;
            if (mouse == null) return;

            if (mouse.leftButton.wasPressedThisFrame)
            {
                dragging = true;
                lastPointer = mouse.position.ReadValue();
            }

            if (mouse.leftButton.wasReleasedThisFrame)
                dragging = false;

            if (dragging)
            {
                var current = mouse.position.ReadValue();
                var delta = current - lastPointer;
                if (delta.sqrMagnitude > 0.01f)
                {
                    yaw -= delta.x * 0.18f;
                    lastPointer = current;
                }
            }
        }

        private void HandleZoom()
        {
            var mouse = Mouse.current;
            if (mouse != null)
                distance = Mathf.Clamp(distance - mouse.scroll.ReadValue().y * 0.012f, 16f, 48f);

            var touchscreen = Touchscreen.current;
            if (touchscreen == null || touchscreen.touches.Count < 2) return;

            var a = touchscreen.touches[0].position.ReadValue();
            var b = touchscreen.touches[1].position.ReadValue();
            var oldA = a - touchscreen.touches[0].delta.ReadValue();
            var oldB = b - touchscreen.touches[1].delta.ReadValue();
            float oldDistance = Vector2.Distance(oldA, oldB);
            float newDistance = Vector2.Distance(a, b);
            if (oldDistance > 0.1f)
                distance = Mathf.Clamp(distance - (newDistance - oldDistance) * 0.035f, 16f, 48f);
        }

        private void UpdateTransform()
        {
            float radians = yaw * Mathf.Deg2Rad;
            Vector3 offset = new(Mathf.Sin(radians) * distance, distance * 0.72f, Mathf.Cos(radians) * distance);
            transform.position = focus + offset;
            transform.LookAt(focus);
            cam.orthographicSize = Mathf.Lerp(8f, 30f, Mathf.InverseLerp(16f, 48f, distance));
        }
    }
}
