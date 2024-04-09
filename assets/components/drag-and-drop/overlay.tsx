import React from 'react';
import {DragOverlay, useDndContext} from '@dnd-kit/core';

interface IProps {
    component: React.ComponentType<{id: string}>,
}

export function Overlay(props: IProps) {
    const {active} = useDndContext();
    const Component = props.component;

    return (
        <DragOverlay>
            {active ? <Component id={active.id.toString()} /> : null}
        </DragOverlay>
    );
}