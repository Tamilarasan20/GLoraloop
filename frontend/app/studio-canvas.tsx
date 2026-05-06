"use client";

import Konva from "konva";
import { useEffect, useRef } from "react";
import { Image, Layer, Rect, Stage, Text } from "react-konva";

type TemplateLayer = {
  type: string;
  content?: string | null;
  src?: string | null;
  color?: string | null;
  font_family?: string | null;
  font_size?: number | null;
  x: number;
  y: number;
  width?: number | null;
  height?: number | null;
  z_index: number;
};

type TemplateReadyData = {
  canvas_width: number;
  canvas_height: number;
  layers: TemplateLayer[];
};

function useCanvasImage(src?: string | null) {
  const imageRef = useRef<HTMLImageElement | null>(null);
  if (src && !imageRef.current) {
    const image = new window.Image();
    image.crossOrigin = "anonymous";
    image.src = src;
    imageRef.current = image;
  }
  return imageRef.current;
}

export default function StudioCanvas({
  template,
  onExporterReady
}: {
  template: TemplateReadyData;
  onExporterReady: (exporter: () => void) => void;
}) {
  const stageRef = useRef<Konva.Stage | null>(null);
  const sortedLayers = [...template.layers].sort((a, b) => a.z_index - b.z_index);

  useEffect(() => {
    onExporterReady(() => {
      const uri = stageRef.current?.toDataURL({ pixelRatio: 2 });
      if (!uri) return;
      const link = document.createElement("a");
      link.download = "laraloop-campaign.png";
      link.href = uri;
      link.click();
    });
  }, [onExporterReady, template]);

  return (
    <Stage
      ref={stageRef}
      width={template.canvas_width}
      height={template.canvas_height}
      className="konva-stage"
      scaleX={0.56}
      scaleY={0.56}
    >
      <Layer>
        {sortedLayers.map((layer, index) => (
          <CanvasLayer key={`${layer.type}-${index}`} layer={layer} />
        ))}
      </Layer>
    </Stage>
  );
}

function CanvasLayer({ layer }: { layer: TemplateLayer }) {
  const image = useCanvasImage(layer.src);

  if (layer.type === "image") {
    return image ? (
      <Image image={image} x={layer.x} y={layer.y} width={layer.width ?? 1080} height={layer.height ?? 1080} />
    ) : (
      <Rect x={layer.x} y={layer.y} width={layer.width ?? 1080} height={layer.height ?? 1080} fill="#f4f0e8" />
    );
  }

  if (layer.type === "rect") {
    return <Rect x={layer.x} y={layer.y} width={layer.width ?? 100} height={layer.height ?? 100} fill={layer.color ?? "#111827"} cornerRadius={8} />;
  }

  return (
    <Text
      x={layer.x}
      y={layer.y}
      width={layer.width ?? 700}
      text={layer.content ?? ""}
      fill={layer.color ?? "#111827"}
      fontFamily={layer.font_family ?? "Inter"}
      fontSize={layer.font_size ?? 32}
      lineHeight={1.08}
      draggable
    />
  );
}
