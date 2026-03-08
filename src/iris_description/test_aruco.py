#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class QuickArUcoTest(Node):
    def __init__(self):
        super().__init__('aruco_test')
        self.bridge = CvBridge()
        
        # Updated for OpenCV 4.7.0+
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # Try both possible camera topics
        self.sub1 = self.create_subscription(Image, '/camera/color/image_raw', self.callback, 10)
        self.sub2 = self.create_subscription(Image, '/camera/image_raw', self.callback, 5)
        
        print("🔍 Looking for ArUco markers...")
        print("📷 Trying camera topics: /camera/color/image_raw, /camera/image_raw")

    def callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect markers using new API
            corners, ids, rejected = self.detector.detectMarkers(gray)
            
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(cv_image, corners, ids)
                print(f"🎯 DETECTED MARKERS: {ids.flatten()}")
                
                # Calculate distance (approximate)
                if len(corners) > 0:
                    marker_corners = corners[0][0]
                    marker_area = cv2.contourArea(marker_corners)
                    distance_est = 50000 / marker_area if marker_area > 0 else 0
                    print(f"📏 Estimated distance: {distance_est:.1f}m")
            else:
                cv2.putText(cv_image, "No ArUco markers detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow('ArUco Detection', cv_image)
            cv2.waitKey(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    rclpy.init()
    node = QuickArUcoTest()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()