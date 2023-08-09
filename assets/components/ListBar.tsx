import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import SearchBar from 'search/components/SearchBar';

class ListBar extends React.Component<any, any> {
    static propTypes: any;
    static defaultProps: any;
    render() {
        return (
            <section className="content-header" data-test-id={this.props.testId}>
                <nav className={classNames(
                    'content-bar navbar flex-nowrap',
                    {
                        'content-bar--side-padding': !this.props.noLeftPadding,
                        'content-bar--no-left-padding': this.props.noLeftPadding,
                    }
                )}>
                    {this.props.children}
                    {!this.props.noSearch &&
                        (<SearchBar
                            setQuery={this.props.setQuery}
                            fetchItems={() => this.props.fetch()}
                            enableQueryAction={this.props.enableQueryAction}
                        />
                        )}
                    <div className="content-bar__right">
                        {this.props.onNewItem && (
                            <button
                                className="nh-button nh-button--primary"
                                data-test-id="new-item-btn"
                                disabled={this.props.disabled}
                                onClick={() => this.props.onNewItem()}
                            >
                                {this.props.buttonText}
                            </button>
                        )}
                    </div>
                </nav>
            </section>
        );
    }
}

ListBar.propTypes = {
    setQuery: PropTypes.func,
    fetch: PropTypes.func,
    buttonText: PropTypes.string.isRequired,
    onNewItem: PropTypes.func,
    children: PropTypes.node,
    noSearch: PropTypes.bool,
    noLeftPadding: PropTypes.bool,
    enableQueryAction: PropTypes.bool,
    testId: PropTypes.string,
    disabled: PropTypes.bool,
};

ListBar.defaultProps = {enableQueryAction: true};

export default ListBar;
