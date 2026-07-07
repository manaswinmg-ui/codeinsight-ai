import * as React from 'react';

interface SkeletonCardProps {
  variant:
    | 'metric'
    | 'table-row'
    | 'finding-card'
    | 'dashboard-stats'
    | 'text'
    | 'chart';
  count?: number;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  variant,
  count = 1,
}) => {
  const renderMetric = () => (
    <div
      className="glass-card animate-pulse"
      style={{
        flex: '1 1 200px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        height: '140px',
        background: 'rgba(255, 255, 255, 0.015)',
        border: '1px solid rgba(255, 255, 255, 0.04)',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            width: '40%',
            height: '14px',
            background: 'rgba(255,255,255,0.06)',
            borderRadius: '4px',
          }}
        />
        <div
          style={{
            width: '24px',
            height: '24px',
            background: 'rgba(255,255,255,0.06)',
            borderRadius: '50%',
          }}
        />
      </div>
      <div
        style={{
          width: '60%',
          height: '28px',
          background: 'rgba(255,255,255,0.08)',
          borderRadius: '4px',
          marginTop: '8px',
        }}
      />
      <div
        style={{
          width: '80%',
          height: '12px',
          background: 'rgba(255,255,255,0.04)',
          borderRadius: '4px',
          marginTop: '4px',
        }}
      />
    </div>
  );

  const renderTableRow = () => (
    <div
      className="animate-pulse"
      style={{
        display: 'flex',
        alignItems: 'center',
        padding: '16px 24px',
        background: 'rgba(255, 255, 255, 0.01)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
        gap: '24px',
      }}
    >
      <div
        style={{
          width: '80px',
          height: '16px',
          background: 'rgba(255,255,255,0.06)',
          borderRadius: '4px',
        }}
      />
      <div
        style={{
          width: '60px',
          height: '16px',
          background: 'rgba(255,255,255,0.04)',
          borderRadius: '4px',
        }}
      />
      <div
        style={{
          flex: 1,
          height: '16px',
          background: 'rgba(255,255,255,0.06)',
          borderRadius: '4px',
        }}
      />
      <div
        style={{
          width: '120px',
          height: '16px',
          background: 'rgba(255,255,255,0.04)',
          borderRadius: '4px',
        }}
      />
      <div
        style={{
          width: '100px',
          height: '28px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '6px',
        }}
      />
    </div>
  );

  const renderFindingCard = () => (
    <div
      className="glass-card animate-pulse"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        padding: '20px',
        background: 'rgba(255, 255, 255, 0.015)',
        border: '1px solid rgba(255, 255, 255, 0.04)',
        borderLeft: '4px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '8px',
        marginBottom: '16px',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            flex: 1,
          }}
        >
          <div
            style={{
              width: '50%',
              height: '18px',
              background: 'rgba(255,255,255,0.08)',
              borderRadius: '4px',
            }}
          />
          <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
            <div
              style={{
                width: '70px',
                height: '18px',
                background: 'rgba(255,255,255,0.04)',
                borderRadius: '4px',
              }}
            />
            <div
              style={{
                width: '90px',
                height: '18px',
                background: 'rgba(255,255,255,0.04)',
                borderRadius: '4px',
              }}
            />
          </div>
        </div>
        <div
          style={{
            width: '60px',
            height: '18px',
            background: 'rgba(255,255,255,0.06)',
            borderRadius: '4px',
          }}
        />
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          marginTop: '4px',
        }}
      >
        <div
          style={{
            width: '100%',
            height: '14px',
            background: 'rgba(255,255,255,0.04)',
            borderRadius: '4px',
          }}
        />
        <div
          style={{
            width: '95%',
            height: '14px',
            background: 'rgba(255,255,255,0.04)',
            borderRadius: '4px',
          }}
        />
        <div
          style={{
            width: '40%',
            height: '14px',
            background: 'rgba(255,255,255,0.04)',
            borderRadius: '4px',
          }}
        />
      </div>
    </div>
  );

  const renderText = () => (
    <div
      className="animate-pulse"
      style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}
    >
      <div
        style={{
          width: '100%',
          height: '14px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '4px',
        }}
      />
      <div
        style={{
          width: '90%',
          height: '14px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '4px',
        }}
      />
      <div
        style={{
          width: '95%',
          height: '14px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '4px',
        }}
      />
      <div
        style={{
          width: '60%',
          height: '14px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '4px',
        }}
      />
    </div>
  );

  const renderChart = () => (
    <div
      className="glass-card animate-pulse"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        background: 'rgba(255,255,255,0.015)',
        border: '1px solid rgba(255,255,255,0.04)',
        height: '220px',
      }}
    >
      <div
        style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          border: '8px solid rgba(255,255,255,0.04)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            width: '60px',
            height: '16px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '4px',
          }}
        />
      </div>
    </div>
  );

  const renderItem = () => {
    switch (variant) {
      case 'metric':
        return renderMetric();
      case 'table-row':
        return renderTableRow();
      case 'finding-card':
        return renderFindingCard();
      case 'text':
        return renderText();
      case 'chart':
        return renderChart();
      case 'dashboard-stats':
        return (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '20px',
            }}
          >
            {[...Array(5)].map((_, i) => (
              <React.Fragment key={i}>{renderMetric()}</React.Fragment>
            ))}
          </div>
        );
      default:
        return renderText();
    }
  };

  return (
    <>
      {[...Array(count)].map((_, i) => (
        <React.Fragment key={i}>{renderItem()}</React.Fragment>
      ))}
    </>
  );
};
