import React from 'react';
import {useSortable} from '@dnd-kit/sortable';
import {CSS} from '@dnd-kit/utilities';

interface IProps<T> {
    id: string;
    template: React.ComponentType<{itemId: string; context: T}>;
    context: T;
}

export function SortableItem<T>(props: IProps<T>) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({id: props.id});

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    const Template = props.template;

    return (
        <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
            {
                isDragging
                    ? (
                        <div style={{opacity: '0.3'}}>
                            <Template itemId={props.id} context={props.context} />
                        </div>
                    )
                    : (
                        <Template itemId={props.id} context={props.context} />
                    )
            }
        </div>
    );
}