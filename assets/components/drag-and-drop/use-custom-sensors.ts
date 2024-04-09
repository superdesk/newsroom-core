import {
    KeyboardSensor,
    MouseSensor,
    PointerActivationConstraint,
    TouchSensor,
    useSensor,
    useSensors,
} from '@dnd-kit/core';

interface IArguments {
    activationConstraint: PointerActivationConstraint;
}

export function useCustomSensors({activationConstraint} : IArguments): ReturnType<typeof useSensors> {
    const mouseSensor = useSensor(MouseSensor, {
        activationConstraint,
    });
    const touchSensor = useSensor(TouchSensor, {
        activationConstraint,
    });
    const keyboardSensor = useSensor(KeyboardSensor, {});

    return useSensors(
        mouseSensor,
        touchSensor,
        keyboardSensor,
    );
}