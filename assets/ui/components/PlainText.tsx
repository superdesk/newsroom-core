import {getPlainTextMemoized} from 'assets/utils';
import * as React from 'react';

interface IProps {
    text: string;
}

export class PlainText extends React.PureComponent<IProps> {
    render() {
        return getPlainTextMemoized(this.props.text) || null;
    }
}
