"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface SliderProps extends React.InputHTMLAttributes<HTMLInputElement> {
  onValueChange?: (value: number[]) => void;
  value?: number[];
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, onValueChange, value, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = parseInt(e.target.value, 10);
      if (onValueChange) {
        onValueChange([val]);
      }
    };

    const currentValue = value && value.length > 0 ? value[0] : (props.defaultValue as number || 50);

    return (
      <div className={cn("relative flex w-full touch-none select-none items-center py-2", className)}>
        <input
          type="range"
          ref={ref}
          className="w-full h-1.5 bg-primary/20 rounded-full appearance-none cursor-pointer accent-primary focus:outline-none"
          value={currentValue}
          onChange={handleChange}
          {...props}
        />
        <style jsx>{`
          input[type='range']::-webkit-slider-thumb {
            appearance: none;
            height: 16px;
            width: 16px;
            border-radius: 50%;
            background: hsl(var(--primary));
            border: 2px solid hsl(var(--background));
            box-shadow: 0 0 10px hsla(var(--primary), 0.3);
            cursor: grab;
          }
          input[type='range']::-webkit-slider-thumb:active {
            cursor: grabbing;
          }
          input[type='range']::-moz-range-thumb {
            height: 16px;
            width: 16px;
            border-radius: 50%;
            background: hsl(var(--primary));
            border: 2px solid hsl(var(--background));
            box-shadow: 0 0 10px hsla(var(--primary), 0.3);
            cursor: grab;
          }
        `}</style>
      </div>
    );
  }
)
Slider.displayName = "Slider"

export { Slider }
