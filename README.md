# Jetsam
Jetsam addresses a major problem in aquatic cleanup: existing systems can harm wildlife and provide little insight into pollution patterns. Jetsam uses a custom AI model to detect wildlife and stop its motor to avoid harm while logging trash type, quantity and GPS data to map pollution hotspots.

# Inspiration
Ghost fishing gear makes up 10% of litter and 46% of the Great Pacific Garbage Patch. At the same time, only 23% of PET plastics like single-use water bottles of the 60 million used daily are recycled. Plastic litter can tangle animals, pollute waterways, and damages ecosystems.
Jetsam uses a dual-pronged approach to detect and collect both PET plastics and fishing nets. Made from recycled materials, including both the fishing nets and plastic water bottles, it embodies a cradle-to-cradle framework. The fishing nets will be recycled into various items in collaboration with local businesses. The PET collected can be converted into BAETA, a carbon absorbing substrate that reduces the emissions of recycling fishing nets. A small portion of plastics acquired will be turned into more Jetsams.

# What it does
Jetsam records where trash is found, how much is detected, what type it is, along with GPS location and time. Over time, this creates a pollution density map to identify hotspots and support smarter environmental planning. It also includes wildlife-aware avoidance, automatically stopping collection when animals are detected. Actions are confidence-based: if TensorFlow detection confidence is above 50%, the system proceeds; if below 50%, it re-evaluates using OpenAI and Claude to prevent false decisions. It skims the surfaces of waterways, scooping up plastic, particularly PET and fishing nets. Jetsam is also fully electric, powered by a propeller motor.

# How we built it
Jetsam is built from various waste produced by TreeHacks around Huang. We collected single-use plastic water bottles, specifically those not placed in recycling, so the landfill and compost bins. We constructed a catamaran raft-like structure that relies on plastic bottles for buoyancy. Using netting from fruit packaging, we created a chamber that traps trash, but lets water currents flow through. Using servo motors and an arduino, we powered a 3D printed propeller pulley system. We added a raspberry pi and camera that detects and identifies objects.

# Challenges we ran into
Too many to count. We could not connect the camera with the raspberry pi despite A LOT of troubleshooting. We also struggled with acquiring all the necessary hardware parts to create multiple motors. As a result, Jetsam P1 has only one propeller, which is enough to move it slowly.

# Accomplishments that we're proud of
We’re proud to have made Jetsam completely out of found materials from around the hackathon. It forced us to adapt along the way, think creatively and resourcefully, and adjust our concept. We’re also super happy that Jetsam floats as intended and can genuinely catch trash.

# What we learned
We learned how to combine hardware and software, working collaboratively across disciplines. In our research, we learned about various existing trash collection robots and how seriously fishing nets contribute to pollution. Finally, by attending workshops and speaking with mentors, we learned to hone in on our niche and pain-point to develop a complete business/product system.

# What's next for Jetsam
In the next prototype, Jetsam will be fully autonomous, with more precise maneuvering. It will also have solar panels to recharge the electrical battery. We will incorporate swarm intelligence so Jetsams can move in a unit to target trash hotspots.

# Built With
adafruit
arduino
c++
folium
google-teachable-machine
matplotlib
numpy
opencv
python
servo-library
tensorflow
