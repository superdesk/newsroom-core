import * as React from 'react';
import PropTypes from 'prop-types';
import {getPlainTextMemoized} from 'utils';

export class PlainText extends React.PureComponent<any, any> {
    render() {
        return getPlainTextMemoized(this.props.text) || null;
    }
}

PlainText.propTypes = {
    text: PropTypes.string,
};
