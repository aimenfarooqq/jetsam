import cv2
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import time
import serial


try:
    arduino = serial.Serial('/dev/cu.usbserial-120', 9600, timeout=1)  # CHANGE THIS PORT
    time.sleep(2)
    print("✅ Arduino connected!")
except Exception as e:
    print(f"⚠️  Arduino not connected: {e}")
    arduino = None


try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

with open('labels.txt', 'r') as f:
    labels = [line.strip().split(' ', 1)[1] for line in f.readlines()]

print(f"Model loaded! Classes: {labels}\n")


TRASH_INFO = {
    "Plastic Bottle": {
        "recycle": "♻️ RECYCLABLE",
        "uses": [
            "Can be turned into BAETA, a carbon-absorbing material",
            "Can be recycled into new bottles",
            "Used to make fleece clothing & jackets",
            "Made into carpet fibers",
            "Converted to plastic lumber",
            "Reused as plant pots or organizers"
        ],
        "impact": "Takes 450 years to decompose",
        "tip": "Rinse before recycling!"
    },
    "Can": {
        "recycle": "♻️ RECYCLABLE", 
        "uses": [
            "Melted down to make new cans",
            "Used in aircraft construction",
            "Made into car parts",
            "Recycled into bike frames",
            "Can be recycled infinitely!"
        ],
        "impact": "Takes 200-500 years to decompose",
        "tip": "Aluminum saves 95% energy when recycled!"
    },
    "Plastic Wrapper": {
        "recycle": "⚠️ HARD TO RECYCLE",
        "uses": [
            "Some stores have special collection bins",
            "Can be made into composite lumber",
            "Used in cement manufacturing as fuel",
            "Converted to waterproof coating",
            "Better: Reduce usage or reuse as bags"
        ],
        "impact": "Takes 10-20 years to decompose",
        "tip": "Check for #2 or #4 plastic - easier to recycle"
    },
    "Plastic Bag": {
        "recycle": "⚠️ SPECIAL RECYCLING",
        "uses": [
            "Return to grocery store collection bins",
            "Made into plastic lumber & decking",
            "Converted to new bags",
            "Used as trash can liners (reuse!)",
            "Made into outdoor furniture"
        ],
        "impact": "Takes 10-1000 years to decompose",
        "tip": "Reuse bags or switch to reusable totes!"
    },
    "Fishing net": {
        "recycle": "⚠️ SPECIAL RECYCLING",
        "uses": [
            "Recycle nets into textiles for clothing",
            "Made into regenerated nylon (ECONYL)",
            "Converted to sunglasses & swimwear",
            "Used in carpets & fashion accessories",
            "Turned into skateboard decks"
        ],
        "impact": "Ghost nets kill 650,000 marine animals/year",
        "tip": "Report abandoned nets to ocean cleanup orgs!"
    },
    "Fish": {
        "recycle": "🐟 NOT TRASH!",
        "uses": [
            "Essential part of ocean ecosystem",
            "Food source for marine life",
            "Helps maintain coral reef health",
            "Important for food chain balance",
            "Indicator species for water quality"
        ],
        "impact": "Protects ocean biodiversity",
        "tip": "Avoid disturbing marine wildlife!"
    }
}

def get_trash_info(trash_type):
    """Get recycling info for trash type"""
    for key in TRASH_INFO.keys():
        if key.lower() in trash_type.lower():
            return TRASH_INFO[key]
    
    return {
        "recycle": "❓ CHECK LOCAL RULES",
        "uses": ["Check with local recycling center"],
        "impact": "Unknown decomposition time",
        "tip": "When in doubt, reduce & reuse!"
    }

def is_fish(trash_type):
    """Check if detected item is actual fish (not fishing net)"""
    return "fish" in trash_type.lower() and "net" not in trash_type.lower()


class HeatmapTracker:
    def __init__(self, width=640, height=480, grid_size=30):
        self.grid_size = grid_size
        self.cols = width // grid_size
        self.rows = height // grid_size
        self.heatmap = np.zeros((self.rows, self.cols))
        self.width = width
        self.height = height
    
    def add_detection(self, x, y):
        """Record detection at position"""
        grid_x = min(x // self.grid_size, self.cols - 1)
        grid_y = min(y // self.grid_size, self.rows - 1)
        self.heatmap[grid_y, grid_x] += 1


class TrashTracker:
    def __init__(self):
        self.detections = []
        self.trash_counts = {label: 0 for label in labels if not is_fish(label)}
        self.shown_info = set()
    
    def add_detection(self, trash_type, confidence):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.detections.append({
            'type': trash_type,
            'confidence': confidence,
            'time': timestamp
        })
        
        if not is_fish(trash_type):
            self.trash_counts[trash_type] = self.trash_counts.get(trash_type, 0) + 1
    
    def generate_combined_visualization(self, heatmap_tracker):
        """Generate combined heatmap + bar chart"""
        if not self.detections:
            print("❌ No detections to visualize!")
            return
        
        # Create figure with 2 subplots side by side
        fig = plt.figure(figsize=(16, 6))
        
        # --- LEFT: HEATMAP ---
        ax1 = plt.subplot(1, 2, 1)
        if np.sum(heatmap_tracker.heatmap) > 0:
            im = ax1.imshow(heatmap_tracker.heatmap, cmap='hot', interpolation='bilinear', aspect='auto')
            ax1.set_title('Trash Detection Heatmap\n(Red = High Density, Blue = Low Density)', 
                         fontsize=14, fontweight='bold')
            ax1.set_xlabel('Horizontal Position')
            ax1.set_ylabel('Vertical Position')
            ax1.invert_yaxis()
            plt.colorbar(im, ax=ax1, label='Detection Count')
            
            max_detections = int(np.max(heatmap_tracker.heatmap))
            ax1.text(0.02, 0.98, f'Max: {max_detections} detections', 
                    transform=ax1.transAxes, fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        else:
            ax1.text(0.5, 0.5, 'No heatmap data', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=14)
        
        # --- RIGHT: BAR CHART ---
        ax2 = plt.subplot(1, 2, 2)
        trash_types = [k for k, v in self.trash_counts.items() if v > 0]
        counts = [self.trash_counts[k] for k in trash_types]
        
        if trash_types:
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
            bars = ax2.bar(trash_types, counts, color=colors[:len(trash_types)])
            ax2.set_title(f'Trash Type Distribution\nTotal: {len(self.detections)} detections', 
                         fontsize=14, fontweight='bold')
            ax2.set_ylabel('Detection Count')
            ax2.set_xlabel('Trash Type')
            ax2.grid(axis='y', alpha=0.3)
            
            # Add count labels on bars
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                        f'{int(count)}',
                        ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            # Rotate labels if needed
            if len(trash_types) > 3:
                ax2.set_xticklabels(trash_types, rotation=15, ha='right')
        else:
            ax2.text(0.5, 0.5, 'No trash detected', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=14)
            ax2.set_title('Trash Type Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        
        filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n📊 Combined visualization saved: {filename}")
        plt.show()
        
        
        print("\n" + "="*60)
        print("🗑️  DETECTION SUMMARY")
        print("="*60)
        print(f"Total detections: {len(self.detections)}")
        for trash_type, count in sorted(self.trash_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / len(self.detections) * 100) if self.detections else 0
                print(f"  • {trash_type}: {count} ({percentage:.1f}%)")
        print("="*60)

def main():
    
    print("Testing camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_ANY)
    
    if not cap.isOpened():
        print("❌ Camera 0 failed, trying camera 1...")
        cap = cv2.VideoCapture(1, cv2.CAP_ANY)
    
    if not cap.isOpened():
        print("❌ No camera found!")
        return
    
    print("✅ Camera connected!")
    print("⏳ Warming up camera...")
    
    
    time.sleep(2)
    
    
    for attempt in range(5):
        ret, test_frame = cap.read()
        if ret:
            print(f"✅ Camera ready! Frame size: {test_frame.shape}")
            height, width = test_frame.shape[:2]
            heatmap_tracker = HeatmapTracker(width, height)
            break
        else:
            print(f"⏳ Attempt {attempt+1}/5...")
            time.sleep(0.5)
    else:
        print("❌ Camera not responding after 5 attempts")
        print("Try: System Settings → Privacy & Security → Camera")
        print("      Enable camera access for Terminal/Python")
        cap.release()
        return
    
    tracker = TrashTracker()
    last_detection = 0
    last_info_display = 0
    current_info = None
    info_display_time = 5
    
    print("\n🎥 Starting Trash Detection")
    print("Press 'q' to quit and see heatmap + graph")
    print("Press 'i' to see info about detected item\n")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Frame read failed at frame {frame_count}")
            time.sleep(0.1)
            continue
        
        frame_count += 1
        current_time = time.time()
        height, width = frame.shape[:2]
        
        
        img = cv2.resize(frame, (224, 224))
        img = np.expand_dims(img, axis=0)
        img = (img.astype(np.float32) / 127.5) - 1
        
        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        
        class_index = np.argmax(predictions)
        trash_type = labels[class_index]
        confidence = predictions[class_index]
        
        
        if confidence > 0.7 and current_time - last_detection > 2:
            if not is_fish(trash_type):
                tracker.add_detection(trash_type, confidence)
                
                center_x = width // 2
                center_y = height // 2
                heatmap_tracker.add_detection(center_x, center_y)
            
            last_detection = current_time
            
            if trash_type not in tracker.shown_info:
                current_info = get_trash_info(trash_type)
                last_info_display = current_time
                tracker.shown_info.add(trash_type)
                
                print(f"\n{'='*60}")
                print(f"📍 {trash_type.upper()} DETECTED!")
                print(f"{'='*60}")
                print(f"{current_info['recycle']}")
                print(f"\n💡 Can be used for:")
                for use in current_info['uses']:
                    print(f"  • {use}")
                print(f"\n⏱️  Impact: {current_info['impact']}")
                print(f"💚 Tip: {current_info['tip']}")
                print(f"{'='*60}\n")
        
        
        if is_fish(trash_type) and confidence > 0.6:
            color = (0, 0, 255)
            status = "🐟 FISH - PROTECT!"
            
            if arduino:
                arduino.write(b'0')
        else:
            color = (0, 255, 0)
            status = trash_type.upper()
            
            if arduino:
                arduino.write(b'1')
        
        cv2.putText(frame, status, (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(frame, f"{confidence*100:.0f}%", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, f"Trash: {len(tracker.detections)}", (20, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        cv2.putText(frame, f"Frame: {frame_count}", (width-150, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        
        
        if current_info and (current_time - last_info_display) < info_display_time:
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 160), (width-10, 400), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            y = 185
            cv2.putText(frame, current_info['recycle'], (20, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 30
            cv2.putText(frame, "Can be used for:", (20, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 25
            
            for use in current_info['uses'][:3]:
                use_short = use if len(use) < 50 else use[:47] + "..."
                cv2.putText(frame, f"• {use_short}", (25, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                y += 20
            
            y += 10
            cv2.putText(frame, f"Tip: {current_info['tip']}", (20, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 255, 100), 1)
        
        cv2.imshow('Trash Detection', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('i') and confidence > 0.5:
            current_info = get_trash_info(trash_type)
            last_info_display = current_time
    
    print(f"\nTotal frames processed: {frame_count}")
    
    
    if arduino:
        arduino.write(b'0')  
        arduino.close()
        print("Arduino connection closed")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n🔄 Generating visualization...")
    tracker.generate_combined_visualization(heatmap_tracker)

if __name__ == "__main__":
    main()