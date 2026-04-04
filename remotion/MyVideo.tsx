import { AbsoluteFill, Sequence, useCurrentFrame, staticFile, Video, Audio, Img, useVideoConfig} from "@remotion/player";
import {interpolate, spring} from "remotion";

const Facts = [
  {
    animal: "Dolphin",
    emoji: "🐬",
    fact: "Did you know? Dolphins can recognize themselves in mirrors!",
    stat: "10,000x",
    statLabel: "better smell than humans"
  },
  {
    animal: "Cat",
    emoji: "🐱",
    fact: "Cats spend 70% of their lives sleeping!",
    stat: "13 years",
    statLabel: "out of 18 year lifespan"
  },
  {
    animal: "Cow",
    emoji: "🐄",
    fact: "Cows have best friends and get stressed when separated!",
    stat: "3",
    statLabel: "hearts - an octopus has"
  }
];

export const MyVideo: React.FC<{factIndex: number}> = ({factIndex}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  
  const fact = Facts[factIndex % Facts.length];
  
  // Text fade in
  const textOpacity = interpolate(frame, [0, 30], [0, 1], {extrapolateRight: "clamp"});
  
  // Subtitle slide up
  const subtitleY = interpolate(frame, [60, 90], [50, 0], {extrapolateRight: "clamp"});
  
  // CTA pulse at end
  const ctaScale = frame > 420 ? interpolate(frame, [420, 450], [1, 1.1], {extrapolateRight: "clamp"}) : 1;
  
  return (
    <AbsoluteFill style={{backgroundColor: "#0a0a0f"}}>
      {/* Video background - use first stock clip */}
      <Video
        src={staticFile("../stock/pexels_5764223.mp4")}
        startFrom={0}
        endAt={450}
        style={{width: "100%", height: "100%", objectFit: "cover"}}
      />
      
      {/* Dark gradient overlay */}
      <div style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 200,
        background: "linear-gradient(to bottom, rgba(0,0,0,0.8), transparent)"
      }} />
      
      {/* Main fact */}
      <div style={{
        position: "absolute",
        top: 60,
        left: 40,
        right: 40,
        opacity: textOpacity,
        textAlign: "center"
      }}>
        <div style={{fontSize: 48, color: "white", fontWeight: "bold", marginBottom: 20}}>
          {fact.emoji} {fact.animal} Facts
        </div>
        <div style={{fontSize: 36, color: "#ff6b9d", fontWeight: "bold"}}>
          {fact.fact}
        </div>
      </div>
      
      {/* Stat highlight */}
      {frame > 60 && (
        <div style={{
          position: "absolute",
          top: subtitleY + 200,
          left: 40,
          right: 40,
          textAlign: "center"
        }}>
          <div style={{fontSize: 72, color: "#ffd93d", fontWeight: "bold"}}>
            {fact.stat}
          </div>
          <div style={{fontSize: 28, color: "white", opacity: 0.9}}>
            {fact.statLabel}
          </div>
        </div>
      )}
      
      {/* CTA at end */}
      {frame > 360 && (
        <div style={{
          position: "absolute",
          bottom: 100,
          left: 0,
          right: 0,
          textAlign: "center",
          transform: `scale(${ctaScale})`
        }}>
          <div style={{
            display: "inline-block",
            backgroundColor: "#ff6b9d",
            padding: "20px 40px",
            borderRadius: 50,
            fontSize: 32,
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
