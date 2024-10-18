import {Placement} from 'popper.js';
import * as React from 'react';
import {Popover} from 'reactstrap';

interface IProps {
    children(toggle: () => void): React.ReactNode;
    placement: Placement;
    component: React.ComponentType<{closePopup(): void}>;
}

interface IState {
    isOpen: boolean;
}

export class Popup extends React.PureComponent<IProps, IState> {
    elem: HTMLElement | undefined;
    referenceElem: HTMLElement | undefined;
    constructor(props: any) {
        super(props);

        this.state = {
            isOpen: false,
        };

        this.toggle = this.toggle.bind(this);
    }

    toggle() {
        this.setState({
            isOpen: !this.state.isOpen,
        });
    }

    render() {
        const {component: Component} = this.props;

        return (
            <>
                <div
                    ref={(elem: any) => this.referenceElem = elem}
                >
                    {this.props.children(this.toggle)}
                </div>

                {this.referenceElem && (
                    <Popover
                        className="action-popover"
                        target={this.referenceElem}
                        isOpen={this.state.isOpen}
                        placement={this.props.placement ?? 'auto'}
                    >
                        <Component closePopup={this.toggle} />
                    </Popover>
                )}
            </>
        );
    }
}
