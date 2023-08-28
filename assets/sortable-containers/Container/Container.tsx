import React, {forwardRef} from 'react';
import classNames from 'classnames';

import {Handle} from '../Handle';
import {Remove} from '../Remove';

import './Container.module.css';

export interface IContainerProps {
  children: React.ReactNode;
  label?: string;
  style?: React.CSSProperties;
  horizontal?: boolean;
  hover?: boolean;
  handleProps?: React.HTMLAttributes<any>;
  scrollable?: boolean;
  shadow?: boolean;
  placeholder?: boolean;
  unstyled?: boolean;
  onClick?(): void;
  onRemove?(): void;
}

export const Container = forwardRef<HTMLDivElement, IContainerProps>(({
    children,
    handleProps,
    horizontal,
    hover,
    onClick,
    onRemove,
    label,
    placeholder,
    style,
    scrollable,
    shadow,
    unstyled,
    ...props
}: IContainerProps, ref) => {
    const Component = onClick ? 'button' : 'div';

    return (
        <Component
            {...props}
            ref={ref}
            style={
          {
              ...style,
              '--columns': 1,
          } as React.CSSProperties
            }
            className={classNames(
                'Container',
                unstyled && 'unstyled',
                horizontal && 'horizontal',
                hover && 'hover',
                placeholder && 'placeholder',
                scrollable && 'scrollable',
                shadow && 'shadow',
            )}
            onClick={onClick}
            tabIndex={onClick ? 0 : undefined}
        >
            {label ? (
                <div>
                    {label}
                    <div>
                        {onRemove ? <Remove onClick={onRemove} /> : undefined}
                        <Handle {...handleProps} />
                    </div>
                </div>
            ) : null}
            {placeholder ? children : <ul>{children}</ul>}
        </Component>
    );
}
);
