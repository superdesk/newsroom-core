import * as React from 'react';
import {Spacer} from '@superdesk/common';

interface IProps {
    children: Array<React.ReactNode>;
}

export class LabelGroup extends React.PureComponent<IProps> {
    render() {
        return (
            <Spacer gap='4' noGrow>
                {this.props.children}
            </Spacer>
        );
    }
}
