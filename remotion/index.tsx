import React from "react";
import {AbsoluteFill, useCurrentFrame, staticFile, Video, interpolate} from "remotion";

const MyComposition: React.FC<{factIndex?: number}> = ({factIndex = 0}) => {
  const frame = useCurrentFrame();
  
  const facts = [
    {emoji: "🐬", animal: "Dolphin", fact: "Dolphins recognize themselves in mirrors!"},
    {emoji: "🐱", animal: "Cat", fact: "Cats spend 70% of their lives sleeping!"},
    {emoji: "🐄", animal: "Cow", fact: "Cows have best friends!"}
  ];
  
  const fact = facts[factIndex % facts.length];
  const textAlpha = interpolate(frame, [0, 30], [0, 1], {extrapolateRight: "clamp"});
  const slideUp = interpolate(frame, [30, 60], [30, 0], {extrapolateRight: "clamp"});
  
  return (
    <AbsoluteFill style={{backgroundColor: "#0a0a0f"}}>
      <Video
        src={staticFile("../stock/pexels_5764223.mp4")}
        startFrom={0}
        durationInFrames={450}
        style={{width: "100%", height: "100%", objectFit: "cover"}}
      />
      
      <div style={{
        position: "absolute",
        top: 0, left: 0, right: 0, height: 180,
        background: "linear-gradient(to bottom, rgba(0,0,0,0.9), transparent)"
      }} />
      
      <div style={{
        position: "absolute",
        top: 50 + slideUp,
        left: 30, right: 30, textAlign: "center",
        opacity: textAlpha
      }}>
        <div style={{fontSize: 56, color: "white", fontWeight: "bold", marginBottom: 16}}>
          {fact.emoji} {fact.animal} Facts
        </div>
        <div style={{fontSize: 38, color: "#ff6b9d", fontWeight: "bold"}}>
          {fact.fact}
        </div>
      </div>
      
      {frame > 380 && (
        <div style={{
          position: "absolute",
          bottom: 120, left: 0, right: 0, textAlign: "center"
        }}>
          <div style={{
            display: "inline-block",
            backgroundColor: "#ff6b9d",
            padding: "24px 48px",
            borderRadius: 50,
            fontSize: 36,
            color: "white",
            fontWeight: "bold"
          }}>
            ❤️ Subscribe for more!
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

export default MyComposition;
