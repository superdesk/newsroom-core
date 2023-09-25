import React from 'react';

interface IProps {
    id: string;
}

export function MainItem(props: IProps) {
    return (
        <div
            style={{
                border: '1px solid red',
                marginTop: 6,
                marginBottom: 6,
                padding: 10,
            }}
        >
            {props.id}
        </div>
    );
}