import React, {useState} from 'react';

interface IProps {
    initiallyOpen?: boolean;
    name?: string;
    testId: string;
    children: JSX.Element;
}

export function FormSection({initiallyOpen, name, testId, children}: IProps) {
    const [opened, setOpened] = useState(initiallyOpen ?? name == null);

    return (
        <div className="nh-flex__column" data-test-id={testId}>
            <div
                className="list-item__preview-collapsible"
                data-test-id="toggle-btn"
                onClick={() => setOpened(!opened)}
            >
                <div className="list-item__preview-collapsible-header">
                    {opened ? (
                        <i className="icon--arrow-right icon--gray-dark icon--rotate-90"></i>
                    ) : (
                        <i className="icon--arrow-right icon--gray-dark"></i>
                    )}
                    <h3>{name}</h3>
                </div>
            </div>
            <div>
                {opened ? (children) : null}
            </div>
        </div>
    );
}
